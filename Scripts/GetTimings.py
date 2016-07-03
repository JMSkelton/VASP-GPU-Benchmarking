# GetTimings.py by J. M. Skelton


import argparse;
import os;

from Shared import CollectResults;


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Extract timing information and final total energy from the output files in a VASP directory.");
    
    parser.set_defaults(
        SkipSCFCycles = 0
        );    
    
    parser.add_argument(
        metavar = "vasp_dir", type = str, nargs = '+',
        dest = 'VASPDirectories',
        help = "VASP directories to process"
        );
    
    parser.add_argument(
        "--skip_scf_cycles",
        type = int, dest = 'SkipSCFCycles',
        help = "exclude the first N SCF cycles from the average (default: 0)"
        );
    
    args = parser.parse_args();
    
    for vaspDirectory in args.VASPDirectories:
        if os.path.isdir(vaspDirectory):
            print("Analysing \"{0}\"...".format(vaspDirectory));
            
            numSCFSteps, tSCFAve, tElapsed, finalTotalEnergy = CollectResults(vaspDirectory, outcarSkipSCFCycles = args.SkipSCFCycles);
                    
            if numSCFSteps != None and tSCFAve != None and tElapsed != None and finalTotalEnergy != None:
                print("  -> # SCF steps: {0}".format(numSCFSteps));
                print("  -> Avgerage t_SCF [s]: {0:.2f}".format(tSCFAve));
                print("  -> Elapsed time [s]: {0:.2f}".format(tElapsed));
                print("  -> Final E_0 [eV]: {0:.8f}".format(finalTotalEnergy));
            else:
                print("  -> Failed to collect data... please check the folder is a valid VASP directory");
        else:
            print("\"{0}\" is not a directory -> skipping".format(vaspDirectory));
        
        print("");
