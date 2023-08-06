Terminal IPython options
========================


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

TerminalIPythonApp.display_banner : Bool
    Default: ``True``

    Whether to display a banner upon starting IPython.

TerminalIPythonApp.force_interact : Bool
    Default: ``False``

    If a command or file is given via the command-line,
    e.g. 'ipython foo.py', start an interactive shell after executing the
    file or command.

TerminalIPythonApp.interactive_shell_class : Type
    Default: ``'IPython.terminal.interactiveshell.TerminalInteractiveShell'``

    Class to use to instantiate the TerminalInteractiveShell object. Useful for custom Frontends

TerminalIPythonApp.quick : Bool
    Default: ``False``

    Start IPython quickly by skipping the loading of config files.

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

TerminalInteractiveShell.confirm_exit : Bool
    Default: ``True``

    
    Set to confirm when you try to exit IPython with an EOF (Control-D
    in Unix, Control-Z/Enter in Windows). By typing 'exit' or 'quit',
    you can force a direct exit without any confirmation.

TerminalInteractiveShell.display_completions : 'column'|'multicolumn'|'readlinelike'
    Default: ``'multicolumn'``

    Options for displaying tab completions, 'column', 'multicolumn', and 'readlinelike'. These options are for `prompt_toolkit`, see `prompt_toolkit` documentation for more information.

TerminalInteractiveShell.editing_mode : Unicode
    Default: ``'emacs'``

    Shortcut style to use at the prompt. 'vi' or 'emacs'.

TerminalInteractiveShell.editor : Unicode
    Default: ``'vi'``

    Set the editor used by IPython (default to $EDITOR/vi/notepad).

TerminalInteractiveShell.enable_history_search : Bool
    Default: ``True``

    Allows to enable/disable the prompt toolkit history search

TerminalInteractiveShell.extra_open_editor_shortcuts : Bool
    Default: ``False``

    Enable vi (v) or Emacs (C-X C-E) shortcuts to open an external editor. This is in addition to the F2 binding, which is always enabled.

TerminalInteractiveShell.handle_return : Any
    Default: ``None``

    Provide an alternative handler to be called when the user presses Return. This is an advanced option intended for debugging, which may be changed or removed in later releases.

TerminalInteractiveShell.highlight_matching_brackets : Bool
    Default: ``True``

    Highlight matching brackets.

TerminalInteractiveShell.highlighting_style : Union
    Default: ``traitlets.Undefined``

    The name or class of a Pygments style to use for syntax
    highlighting. To see available styles, run `pygmentize -L styles`.

TerminalInteractiveShell.highlighting_style_overrides : Dict
    Default: ``{}``

    Override highlighting format for specific tokens

TerminalInteractiveShell.mouse_support : Bool
    Default: ``False``

    Enable mouse support in the prompt
    (Note: prevents selecting text with the mouse)

TerminalInteractiveShell.prompts_class : Type
    Default: ``'IPython.terminal.prompts.Prompts'``

    Class used to generate Prompt token for prompt_toolkit

TerminalInteractiveShell.simple_prompt : Bool
    Default: ``False``

    Use `raw_input` for the REPL, without completion and prompt colors.
    
    Useful when controlling IPython as a subprocess, and piping STDIN/OUT/ERR. Known usage are:
    IPython own testing machinery, and emacs inferior-shell integration through elpy.
    
    This mode default to `True` if the `IPY_TEST_SIMPLE_PROMPT`
    environment variable is set, or the current terminal is not a tty.

TerminalInteractiveShell.space_for_menu : Int
    Default: ``6``

    Number of line at the bottom of the screen to reserve for the completion menu

TerminalInteractiveShell.term_title : Bool
    Default: ``True``

    Automatically set the terminal title

TerminalInteractiveShell.term_title_format : Unicode
    Default: ``'IPython: {cwd}'``

    Customize the terminal title format.  This is a python format string. Available substitutions are: {cwd}.

TerminalInteractiveShell.true_color : Bool
    Default: ``False``

    Use 24bit colors instead of 256 colors in prompt highlighting. If your terminal supports true color, the following command should print 'TRUECOLOR' in orange: printf "\x1b[38;2;255;100;0mTRUECOLOR\x1b[0m\n"


HistoryAccessor.connection_options : Dict
    Default: ``{}``

    Options for configuring the SQLite connection
    
    These options are passed as keyword args to sqlite3.connect
    when establishing database connections.


HistoryAccessor.enabled : Bool
    Default: ``True``

    enable the SQLite history
    
    set enabled=False to disable the SQLite history,
    in which case there will be no stored history, no SQLite connection,
    and no background saving thread.  This may be necessary in some
    threaded environments where IPython is embedded.


HistoryAccessor.hist_file : Unicode
    Default: ``''``

    Path to file to use for SQLite history database.
    
    By default, IPython will put the history database in the IPython
    profile directory.  If you would rather share one history among
    profiles, you can set this value in each, so that they are consistent.
    
    Due to an issue with fcntl, SQLite is known to misbehave on some NFS
    mounts.  If you see IPython hanging, try setting this to something on a
    local disk, e.g::
    
        ipython --HistoryManager.hist_file=/tmp/ipython_hist.sqlite
    
    you can also use the specific value `:memory:` (including the colon
    at both end but not the back ticks), to avoid creating an history file.
    


HistoryManager.db_cache_size : Int
    Default: ``0``

    Write to database every x commands (higher values save disk access & power).
    Values of 1 or less effectively disable caching.

HistoryManager.db_log_output : Bool
    Default: ``False``

    Should the history database include output? (default: no)

ProfileDir.location : Unicode
    Default: ``''``

    Set the profile location directly. This overrides the logic used by the
    `profile` option.

BaseFormatter.deferred_printers : Dict
    Default: ``{}``

    No description

BaseFormatter.enabled : Bool
    Default: ``True``

    No description

BaseFormatter.singleton_printers : Dict
    Default: ``{}``

    No description

BaseFormatter.type_printers : Dict
    Default: ``{}``

    No description

PlainTextFormatter.float_precision : CUnicode
    Default: ``''``

    No description

PlainTextFormatter.max_seq_length : Int
    Default: ``1000``

    Truncate large collections (lists, dicts, tuples, sets) to this size.
    
    Set to 0 to disable truncation.


PlainTextFormatter.max_width : Int
    Default: ``79``

    No description

PlainTextFormatter.newline : Unicode
    Default: ``'\\n'``

    No description

PlainTextFormatter.pprint : Bool
    Default: ``True``

    No description

PlainTextFormatter.verbose : Bool
    Default: ``False``

    No description

Completer.backslash_combining_completions : Bool
    Default: ``True``

    Enable unicode completions, e.g. \alpha<tab> . Includes completion of latex commands, unicode names, and expanding unicode characters back to latex commands.

Completer.debug : Bool
    Default: ``False``

    Enable debug for the Completer. Mostly print extra information for experimental jedi integration.

Completer.greedy : Bool
    Default: ``False``

    Activate greedy completion
    PENDING DEPRECTION. this is now mostly taken care of with Jedi.
    
    This will enable completion on elements of lists, results of function calls, etc.,
    but can be unsafe because the code is actually evaluated on TAB.


Completer.jedi_compute_type_timeout : Int
    Default: ``400``

    Experimental: restrict time (in milliseconds) during which Jedi can compute types.
    Set to 0 to stop computing types. Non-zero value lower than 100ms may hurt
    performance by preventing jedi to build its cache.


Completer.use_jedi : Bool
    Default: ``True``

    Experimental: Use Jedi to generate autocompletions. Default to True if jedi is installed

IPCompleter.limit_to__all__ : Bool
    Default: ``False``

    
    DEPRECATED as of version 5.0.
    
    Instruct the completer to use __all__ for the completion
    
    Specifically, when completing on ``object.<tab>``.
    
    When True: only those names in obj.__all__ will be included.
    
    When False [default]: the __all__ attribute is ignored


IPCompleter.merge_completions : Bool
    Default: ``True``

    Whether to merge completion results into a single list
    
    If False, only the completion results from the first non-empty
    completer will be returned.


IPCompleter.omit__names : 0|1|2
    Default: ``2``

    Instruct the completer to omit private method names
    
    Specifically, when completing on ``object.<tab>``.
    
    When 2 [default]: all names that start with '_' will be excluded.
    
    When 1: all 'magic' names (``__foo__``) will be excluded.
    
    When 0: nothing will be excluded.



ScriptMagics.script_magics : List
    Default: ``[]``

    Extra script cell magics to define
    
    This generates simple wrappers of `%%script foo` as `%%foo`.
    
    If you want to add script magics that aren't on your path,
    specify them in script_paths


ScriptMagics.script_paths : Dict
    Default: ``{}``

    Dict mapping short 'ruby' names to full paths, such as '/opt/secret/bin/ruby'
    
    Only necessary for items in script_magics where the default path will not
    find the right interpreter.


LoggingMagics.quiet : Bool
    Default: ``False``

    
    Suppress output of log state when logging is enabled


StoreMagics.autorestore : Bool
    Default: ``False``

    If True, any %store-d variables will be automatically restored
    when IPython starts.

