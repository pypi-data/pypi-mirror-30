# Guild tests

Guild tests can be run with the `check` command using the `-T` option
(`-n` here skips the general check info as we're just interested in
tests).

    >>> run("guild check -nT") # doctest: +REPORT_UDIFF
    internal tests:
      config:                  ok
      cpu-plugin:              ok
      dependencies:            ok
      disk-plugin:             ok
      entry-points:            ok
      guildfiles:              ok
      help:                    ok
      imports:                 ok
      includes:                ok
      logging:                 ok
      main-bootstrap:          ok
      memory-plugin:           ok
      models:                  ok
      namespaces:              ok
      ops:                     ok
      package:                 ok
      plugin-python-utils:     ok
      plugin-utils:            ok
      plugins:                 ok
      run-output:              ok
      runs:                    ok
      tables:                  ok
      utils:                   ok
      var:                     ok
    <exit 0>
