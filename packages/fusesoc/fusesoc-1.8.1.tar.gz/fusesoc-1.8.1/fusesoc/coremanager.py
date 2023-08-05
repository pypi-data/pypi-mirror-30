import logging
import os
import shutil

from okonomiyaki.versions import EnpkgVersion

from simplesat.constraints import PrettyPackageStringParser, Requirement
from simplesat.dependency_solver import DependencySolver
from simplesat.errors import NoPackageFound, SatisfiabilityError
from simplesat.pool import Pool
from simplesat.repository import Repository
from simplesat.request import Request

from fusesoc.core import Core

logger = logging.getLogger(__name__)

class DependencyError(Exception):
    def __init__(self, value, msg=""):
        self.value = value
        self.msg = msg
    def __str__(self):
        return repr(self.value)

class CoreDB(object):
    def __init__(self):
        self._cores = {}

    #simplesat doesn't allow ':', '-' or leading '_'
    def _package_name(self, vlnv):
        _name = "{}_{}_{}".format(vlnv.vendor,
                                  vlnv.library,
                                  vlnv.name).lstrip("_")
        return _name.replace('-','__')

    def _package_version(self, vlnv):
        return "{}-{}".format(vlnv.version,
                              vlnv.revision)

    def _parse_depend(self, depends):
        #FIXME: Handle conflicts
        deps = []
        _s = "{} {} {}"
        for d in depends:
            deps.append(_s.format(self._package_name(d),
                                  d.relation,
                                  self._package_version(d)))
        return ", ".join(deps)

    def add(self, core):
        name = str(core.name)
        logger.debug("Adding core " + name)
        if name in self._cores:
            _s = "Replacing {} in {} with the version found in {}"
            logger.debug(_s.format(name,
                                   self._cores[name].core_root,
                                   core.core_root))
        self._cores[name] = core

    def find(self, vlnv=None):
        if vlnv:
            found = self._solve(vlnv, only_matching_vlnv=True)[-1]
        else:
            found = list(self._cores.values())
        return found

    def solve(self, top_core, flags):
        return self._solve(top_core, flags)

    def _solve(self, top_core, flags={}, only_matching_vlnv=False):
        def eq_vln(this, that):
            return \
                this.vendor  == that.vendor and \
                this.library == that.library and \
                this.name    == that.name

        repo = Repository()
        _flags = flags.copy()
        for core in self._cores.values():
            if only_matching_vlnv:
                if not eq_vln(core.name, top_core):
                    continue

            package_str = "{} {}-{}".format(self._package_name(core.name),
                                            core.name.version,
                                            core.name.revision)
            if not only_matching_vlnv:
                _flags['is_toplevel'] = (core.name == top_core)
                _depends = core.get_depends(_flags)
                if _depends:
                    _s = "; depends ( {} )"
                    package_str += _s.format(self._parse_depend(_depends))
            parser = PrettyPackageStringParser(EnpkgVersion.from_string)

            package = parser.parse_to_package(package_str)
            package.core = core

            repo.add_package(package)

        request = Request()
        _top_dep = "{} {} {}".format(self._package_name(top_core),
                                     top_core.relation,
                                     self._package_version(top_core))
        requirement = Requirement._from_string(_top_dep)
        request.install(requirement)
        installed_repository = Repository()
        pool = Pool([repo])
        pool.add_repository(installed_repository)
        solver = DependencySolver(pool, [repo], installed_repository)

        try:
            transaction = solver.solve(request)
        except SatisfiabilityError as e:
            raise DependencyError(top_core.name,
                                  msg=e.unsat.to_string(pool))
        except NoPackageFound as e:
            raise DependencyError(top_core.name)

        return [op.package.core for op in transaction.operations]

class CoreManager(object):
    _instance = None

    def __init__(self, config):
        self.config = config
        self._cores_root = []
        self.db = CoreDB()

    def load_core(self, file):
        if os.path.exists(file):
            try:
                core = Core(file, self.config.cache_root, self.config.build_root)
                self.db.add(core)
            except SyntaxError as e:
                w = "Parse error. Ignoring file " + file + ": " + e.msg
                logger.warning(w)
            except ImportError as e:
                logger.warning('Failed to register "{}" due to unknown provider: {}'.format(file, str(e)))

    def load_cores(self, path):
        if path:
            logger.debug("Checking for cores in " + path)
        if os.path.isdir(path) == False:
            raise IOError(path + " is not a directory")
        for root, dirs, files in os.walk(path, followlinks=True):
            for f in files:
                if f.endswith('.core'):
                    d = os.path.basename(root)
                    self.load_core(os.path.join(root, f))
                    del dirs[:]

    def add_cores_root(self, path):
        if path is None:
            return
        elif not isinstance(path, list):
            path = [path]
        for p in path:
            if not p:
                # skip empty entries
                continue
            abspath = os.path.abspath(os.path.expanduser(p))
            if not abspath in self._cores_root:
                self.load_cores(os.path.expanduser(p))
                self._cores_root += [abspath]

    def get_cores_root(self):
        return self._cores_root

    def get_depends(self, core, flags):
        logger.debug("Calculating dependencies for {}{} with flags {}".format(core.relation,str(core), str(flags)))
        resolved_core = self.db.find(core)
        deps = self.db.solve(resolved_core.name, flags)
        logger.debug(" Resolved core to {}".format(str(resolved_core.name)))
        logger.debug(" with dependencies " + ', '.join([str(c.name) for c in deps]))
        return deps

    def get_cores(self):
        return {str(x.name) : x for x in self.db.find()}

    def get_core(self, name):
        c = self.db.find(name)
        c.name.relation = "=="
        return c

    def setup(self, vlnv, flags, work_root, export_root=None):
        if os.path.exists(work_root):
            for f in os.listdir(work_root):
                if os.path.isdir(os.path.join(work_root, f)):
                    shutil.rmtree(os.path.join(work_root, f))
                else:
                    os.remove(os.path.join(work_root, f))
        else:
            os.makedirs(work_root)

        logger.debug("Building EDA API")
        def merge_dict(d1, d2):
            for key, value in d2.items():
                if key in d1:
                    d1[key] += value
                else:
                    d1[key] = value

        files        = []
        parameters   = []
        scripts      = {}
        tool_options = {}
        vpi          = []

        cores = self.get_depends(vlnv, flags)

        _flags = flags.copy()
        for core in cores:
            logger.info("Preparing " + str(core.name))
            core.setup()

            logger.debug("Collecting EDA API parameters from {}".format(str(core.name)))
            _flags['is_toplevel'] = (core.name == vlnv)

            #Extract parameters
            for param in core.get_parameters(_flags):
                parameters.append ({
                    'datatype'    : param.datatype,
                    'default'     : param.default,
                    'description' : param.description,
                    'name'        : param.name,
                    'paramtype'   : param.paramtype})

            #Extract tool options
            merge_dict(tool_options, core.get_tool_options(_flags))

            #Extract files
            if export_root:
                files_root = os.path.join(export_root, core.sanitized_name)
                dst_dir = os.path.join(export_root, core.sanitized_name)
                core.export(dst_dir, _flags)
            else:
                files_root = core.files_root

            rel_root = os.path.relpath(files_root, work_root)
            #Extract scripts
            _scripts = core.get_scripts(rel_root, _flags)
            for section in _scripts.values():
                for script in section:
                    script['env']['FILES_ROOT'] = rel_root

            merge_dict(scripts, _scripts)

            for file in core.get_files(_flags):
                if file.copyto:
                    _name = file.copyto
                    dst = os.path.join(work_root, _name)
                    _dstdir = os.path.dirname(dst)
                    if not os.path.exists(_dstdir):
                        os.makedirs(_dstdir)
                    shutil.copy2(os.path.join(files_root, file.name),
                                 dst)
                else:
                    _name = os.path.join(rel_root, file.name)
                files.append({
                    'name'            : _name,
                    'file_type'       : file.file_type,
                    'is_include_file' : file.is_include_file,
                    'logical_name'    : file.logical_name})
            #Extract VPI modules
            for _vpi in core.get_vpi(_flags):
                vpi.append({'name'         : _vpi['name'],
                            'src_files'    : [os.path.join(rel_root, f.name) for f in _vpi['src_files']],
                            'include_dirs' : [os.path.join(rel_root, i) for i in _vpi['include_dirs']],
                            'libs'         : _vpi['libs']})

        top_core = cores[-1]
        return {
            'version'      : '0.1.2',
            'files'        : files,
            'hooks'        : scripts,
            'name'         : top_core.sanitized_name,
            'parameters'   : parameters,
            'tool_options' : {flags['tool'] : tool_options},
            'toplevel'     : top_core.get_toplevel(flags),
            'vpi'          : vpi,
        }

