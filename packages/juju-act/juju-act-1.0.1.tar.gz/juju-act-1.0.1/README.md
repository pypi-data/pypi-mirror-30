# Juju Act

'juju act' is a Juju plugin to improve the actions command line user
experiece. It operates synchronously, combining the built in
`run-action` and `show-action-output` commands into one.

This plugin supports Juju 1.25 and Juju 2.0. When a future version
of Juju gains a --wait argument to the `run-action` command, it is
expected that this plugin will simply wrap that for backwards compatibility.
This work can be tracked at https://bugs.launchpad.net/bugs/1445066

## TODO

* Run an action on the leader in a service, rather than on a specific unit.

* Run an action on all units in a service. Output and exit codes need
  to be combined. Run Parallel (fast), serially (rolling upgrades), or
  user choice?

## Support

'juju act' is maintained on Launchpad at https://launchpad.net/juju-act
by Stuart Bishop <stuart.bishop@canonical.com>. Bugs can be reported
at https://bugs.launchpad.net/juju-act or to the main Juju mailing list.
Code can be found in git at https://git.launchpad.net/juju-act
