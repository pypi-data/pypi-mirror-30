package ifneeded tclHelper 1.0 [subst {
    source $dir/tclHelper.tcl

    package require Tclx
    
    package provide tclHelper 1.0
}]