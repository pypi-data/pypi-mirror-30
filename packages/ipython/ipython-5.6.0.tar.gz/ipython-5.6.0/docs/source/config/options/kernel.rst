IPython kernel options
======================

These options can be used in :file:`ipython_kernel_config.py`. The kernel also respects any options in `ipython_config.py`



ConnectionFileMixin.connection_file : Unicode
    Default: ``''``

    JSON file in which to store connection info [default: kernel-<pid>.json]
    
    This file will contain the IP, ports, and authentication key needed to connect
    clients to this kernel. By default, this file will be created in the security dir
    of the current profile, but can be specified by absolute path.


ConnectionFileMixin.control_port : Int
    Default: ``0``

    set the control (ROUTER) port [default: random]

ConnectionFileMixin.hb_port : Int
    Default: ``0``

    set the heartbeat port [default: random]

ConnectionFileMixin.iopub_port : Int
    Default: ``0``

    set the iopub (PUB) port [default: random]

ConnectionFileMixin.ip : Unicode
    Default: ``''``

    Set the kernel's IP address [default localhost].
    If the IP address is something other than localhost, then
    Consoles on other machines will be able to connect
    to the Kernel, so be careful!

ConnectionFileMixin.shell_port : Int
    Default: ``0``

    set the shell (ROUTER) port [default: random]

ConnectionFileMixin.stdin_port : Int
    Default: ``0``

    set the stdin (ROUTER) port [default: random]

ConnectionFileMixin.transport : 'tcp'|'ipc'
    Default: ``'tcp'``

    No description

InteractiveShellApp.code_to_run : Unicode
    Default: ``''``

    Execute the given command string.

InteractiveShellApp.exec_PYTHONSTARTUP : Bool
    Default: ``True``

    Run the file referenced by the PYTHONSTARTUP environment
    variable at IPython startup.

InteractiveShellApp.exec_files : List
    Default: ``[]``

    List of files to run at IPython startup.

InteractiveShellApp.exec_lines : List
    Default: ``[]``

    lines of code to run at IPython startup.

InteractiveShellApp.extensions : List
    Default: ``[]``

    A list of dotted module names of IPython extensions to load.

InteractiveShellApp.extra_extension : Unicode
    Default: ``''``

    dotted module name of an IPython extension to load.

InteractiveShellApp.file_to_run : Unicode
    Default: ``''``

    A file to be run

InteractiveShellApp.gui : 'glut'|'gtk'|'gtk2'|'gtk3'|'osx'|'pyglet'|'qt'|'qt4'|'qt5'|'tk'|'wx'|'gtk2'|'qt4'
    Default: ``None``

    Enable GUI event loop integration with any of ('glut', 'gtk', 'gtk2', 'gtk3', 'osx', 'pyglet', 'qt', 'qt4', 'qt5', 'tk', 'wx', 'gtk2', 'qt4').

InteractiveShellApp.hide_initial_ns : Bool
    Default: ``True``

    Should variables loaded at startup (by startup files, exec_lines, etc.)
    be hidden from tools like %who?

InteractiveShellApp.matplotlib : 'auto'|'agg'|'gtk'|'gtk3'|'inline'|'ipympl'|'nbagg'|'notebook'|'osx'|'pdf'|'ps'|'qt'|'qt4'|'qt5'|'svg'|'tk'|'widget'|'wx'
    Default: ``None``

    Configure matplotlib for interactive use with
    the default matplotlib backend.

InteractiveShellApp.module_to_run : Unicode
    Default: ``''``

    Run the module as a script.

InteractiveShellApp.pylab : 'auto'|'agg'|'gtk'|'gtk3'|'inline'|'ipympl'|'nbagg'|'notebook'|'osx'|'pdf'|'ps'|'qt'|'qt4'|'qt5'|'svg'|'tk'|'widget'|'wx'
    Default: ``None``

    Pre-load matplotlib and numpy for interactive use,
    selecting a particular matplotlib backend and loop integration.


InteractiveShellApp.pylab_import_all : Bool
    Default: ``True``

    If true, IPython will populate the user namespace with numpy, pylab, etc.
    and an ``import *`` is done from numpy and pylab, when using pylab mode.
    
    When False, pylab mode should not import any names into the user namespace.


InteractiveShellApp.reraise_ipython_extension_failures : Bool
    Default: ``False``

    Reraise exceptions encountered loading IPython extensions?


Application.log_datefmt : Unicode
    Default: ``'%Y-%m-%d %H:%M:%S'``

    The date format used by logging formatters for %(asctime)s

Application.log_format : Unicode
    Default: ``'[%(name)s]%(highlevel)s %(message)s'``

    The Logging format template

Application.log_level : 0|10|20|30|40|50|'DEBUG'|'INFO'|'WARN'|'ERROR'|'CRITICAL'
    Default: ``30``

    Set the log level by value or name.

BaseIPythonApplication.auto_create : Bool
    Default: ``False``

    Whether to create profile dir if it doesn't exist

BaseIPythonApplication.copy_config_files : Bool
    Default: ``False``

    Whether to install the default config files into the profile dir.
    If a new profile is being created, and IPython contains config files for that
    profile, then they will be staged into the new directory.  Otherwise,
    default config files will be automatically generated.


BaseIPythonApplication.extra_config_file : Unicode
    Default: ``''``

    Path to an extra config file to load.
    
    If specified, load this config file in addition to any other IPython config.


BaseIPythonApplication.ipython_dir : Unicode
    Default: ``''``

    
    The name of the IPython directory. This directory is used for logging
    configuration (through profiles), history storage, etc. The default
    is usually $HOME/.ipython. This option can also be specified through
    the environment variable IPYTHONDIR.


BaseIPythonApplication.overwrite : Bool
    Default: ``False``

    Whether to overwrite existing config files when copying

BaseIPythonApplication.profile : Unicode
    Default: ``'default'``

    The IPython profile to use.

BaseIPythonApplication.verbose_crash : Bool
    Default: ``False``

    Create a massive crash report when IPython encounters what may be an
    internal error.  The default is to append a short message to the
    usual traceback

IPKernelApp.displayhook_class : DottedObjectName
    Default: ``'ipykernel.displayhook.ZMQDisplayHook'``

    The importstring for the DisplayHook factory

IPKernelApp.interrupt : Int
    Default: ``0``

    ONLY USED ON WINDOWS
    Interrupt this process when the parent is signaled.


IPKernelApp.kernel_class : Type
    Default: ``'ipykernel.ipkernel.IPythonKernel'``

    The Kernel subclass to be used.
    
    This should allow easy re-use of the IPKernelApp entry point
    to configure and launch kernels other than IPython's own.


IPKernelApp.no_stderr : Bool
    Default: ``False``

    redirect stderr to the null device

IPKernelApp.no_stdout : Bool
    Default: ``False``

    redirect stdout to the null device

IPKernelApp.outstream_class : DottedObjectName
    Default: ``'ipykernel.iostream.OutStream'``

    The importstring for the OutStream factory

IPKernelApp.parent_handle : Int
    Default: ``0``

    kill this process if its parent dies.  On Windows, the argument
    specifies the HANDLE of the parent process, otherwise it is simply boolean.


Kernel._darwin_app_nap : Bool
    Default: ``True``

    Whether to use appnope for compatiblity with OS X App Nap.
    
    Only affects OS X >= 10.9.


Kernel._execute_sleep : Float
    Default: ``0.0005``

    No description

Kernel._poll_interval : Float
    Default: ``0.05``

    No description

IPythonKernel.help_links : List
    Default: ``[{'text': 'Python Reference', 'url': 'https://docs.python.org...``

    No description

IPythonKernel.use_experimental_completions : Bool
    Default: ``True``

    Set this flag to False to deactivate the use of experimental IPython completion APIs.

InteractiveShell.ast_node_interactivity : 'all'|'last'|'last_expr'|'none'|'last_expr_or_assign'
    Default: ``'last_expr'``

    
    'all', 'last', 'last_expr' or 'none', 'last_expr_or_assign' specifying
    which nodes should be run interactively (displaying output from expressions).


InteractiveShell.ast_transformers : List
    Default: ``[]``

    
    A list of ast.NodeTransformer subclass instances, which will be applied
    to user input before code is run.


InteractiveShell.autocall : 0|1|2
    Default: ``0``

    
    Make IPython automatically call any callable object even if you didn't
    type explicit parentheses. For example, 'str 43' becomes 'str(43)'
    automatically. The value can be '0' to disable the feature, '1' for
    'smart' autocall, where it is not applied if there are no more
    arguments on the line, and '2' for 'full' autocall, where all callable
    objects are automatically called (even if no arguments are present).


InteractiveShell.autoindent : Bool
    Default: ``True``

    
    Autoindent IPython code entered interactively.


InteractiveShell.automagic : Bool
    Default: ``True``

    
    Enable magic commands to be called without the leading %.


InteractiveShell.banner1 : Unicode
    Default: ``"Python 3.6.4 (default, Mar 13 2018, 18:18:20) \\nType 'copyri...``

    The part of the banner to be printed before the profile

InteractiveShell.banner2 : Unicode
    Default: ``''``

    The part of the banner to be printed after the profile

InteractiveShell.cache_size : Int
    Default: ``1000``

    
    Set the size of the output cache.  The default is 1000, you can
    change it permanently in your config file.  Setting it to 0 completely
    disables the caching system, and the minimum value accepted is 3 (if
    you provide a value less than 3, it is reset to 0 and a warning is
    issued).  This limit is defined because otherwise you'll spend more
    time re-flushing a too small cache than working


InteractiveShell.color_info : Bool
    Default: ``True``

    
    Use colors for displaying information about objects. Because this
    information is passed through a pager (like 'less'), and some pagers
    get confused with color codes, this capability can be turned off.


InteractiveShell.colors : 'Neutral'|'NoColor'|'LightBG'|'Linux'
    Default: ``'Neutral'``

    Set the color scheme (NoColor, Neutral, Linux, or LightBG).

InteractiveShell.debug : Bool
    Default: ``False``

    No description

InteractiveShell.disable_failing_post_execute : Bool
    Default: ``False``

    Don't call post-execute functions that have failed in the past.

InteractiveShell.display_page : Bool
    Default: ``False``

    If True, anything that would be passed to the pager
    will be displayed as regular output instead.

InteractiveShell.enable_html_pager : Bool
    Default: ``False``

    
    (Provisional API) enables html representation in mime bundles sent
    to pagers.


InteractiveShell.history_length : Int
    Default: ``10000``

    Total length of command history

InteractiveShell.history_load_length : Int
    Default: ``1000``

    
    The number of saved history entries to be loaded
    into the history buffer at startup.


InteractiveShell.ipython_dir : Unicode
    Default: ``''``

    No description

InteractiveShell.logappend : Unicode
    Default: ``''``

    
    Start logging to the given file in append mode.
    Use `logfile` to specify a log file to **overwrite** logs to.


InteractiveShell.logfile : Unicode
    Default: ``''``

    
    The name of the logfile to use.


InteractiveShell.logstart : Bool
    Default: ``False``

    
    Start logging to the default log file in overwrite mode.
    Use `logappend` to specify a log file to **append** logs to.


InteractiveShell.object_info_string_level : 0|1|2
    Default: ``0``

    No description

InteractiveShell.pdb : Bool
    Default: ``False``

    
    Automatically call the pdb debugger after every exception.


InteractiveShell.prompt_in1 : Unicode
    Default: ``'In [\\#]: '``

    Deprecated since IPython 4.0 and ignored since 5.0, set TerminalInteractiveShell.prompts object directly.

InteractiveShell.prompt_in2 : Unicode
    Default: ``'   .\\D.: '``

    Deprecated since IPython 4.0 and ignored since 5.0, set TerminalInteractiveShell.prompts object directly.

InteractiveShell.prompt_out : Unicode
    Default: ``'Out[\\#]: '``

    Deprecated since IPython 4.0 and ignored since 5.0, set TerminalInteractiveShell.prompts object directly.

InteractiveShell.prompts_pad_left : Bool
    Default: ``True``

    Deprecated since IPython 4.0 and ignored since 5.0, set TerminalInteractiveShell.prompts object directly.

InteractiveShell.quiet : Bool
    Default: ``False``

    No description

InteractiveShell.separate_in : SeparateUnicode
    Default: ``'\\n'``

    No description

InteractiveShell.separate_out : SeparateUnicode
    Default: ``''``

    No description

InteractiveShell.separate_out2 : SeparateUnicode
    Default: ``''``

    No description

InteractiveShell.show_rewritten_input : Bool
    Default: ``True``

    Show rewritten input, e.g. for autocall.

InteractiveShell.sphinxify_docstring : Bool
    Default: ``False``

    
    Enables rich html representation of docstrings. (This requires the
    docrepr module).


InteractiveShell.wildcards_case_sensitive : Bool
    Default: ``True``

    No description

InteractiveShell.xmode : 'Context'|'Plain'|'Verbose'
    Default: ``'Context'``

    Switch modes for the IPython exception handlers.


ProfileDir.location : Unicode
    Default: ``''``

    Set the profile location directly. This overrides the logic used by the
    `profile` option.

Session.buffer_threshold : Int
    Default: ``1024``

    Threshold (in bytes) beyond which an object's buffer should be extracted to avoid pickling.

Session.check_pid : Bool
    Default: ``True``

    Whether to check PID to protect against calls after fork.
    
    This check can be disabled if fork-safety is handled elsewhere.


Session.copy_threshold : Int
    Default: ``65536``

    Threshold (in bytes) beyond which a buffer should be sent without copying.

Session.debug : Bool
    Default: ``False``

    Debug output in the Session

Session.digest_history_size : Int
    Default: ``65536``

    The maximum number of digests to remember.
    
    The digest history will be culled when it exceeds this value.


Session.item_threshold : Int
    Default: ``64``

    The maximum number of items for a container to be introspected for custom serialization.
    Containers larger than this are pickled outright.


Session.key : CBytes
    Default: ``b''``

    execution key, for signing messages.

Session.keyfile : Unicode
    Default: ``''``

    path to file containing execution key.

Session.metadata : Dict
    Default: ``{}``

    Metadata dictionary, which serves as the default top-level metadata dict for each message.

Session.packer : DottedObjectName
    Default: ``'json'``

    The name of the packer for serializing messages.
    Should be one of 'json', 'pickle', or an import name
    for a custom callable serializer.

Session.session : CUnicode
    Default: ``''``

    The UUID identifying this session.

Session.signature_scheme : Unicode
    Default: ``'hmac-sha256'``

    The digest scheme used to construct the message signatures.
    Must have the form 'hmac-HASH'.

Session.unpacker : DottedObjectName
    Default: ``'json'``

    The name of the unpacker for unserializing messages.
    Only used with custom functions for `packer`.

Session.username : Unicode
    Default: ``'takluyver'``

    Username for the Session. Default is your system username.
