# CPUTest.py by J. M. Skelton


# Number of MPI processes.

NumProcesses = 16;

# Values of KPAR to test.
# If set to None or an empty list, it will be given a default value of [1].

TestKPARValues = [1];

# Values of NPAR to test.
# If set to None or an empty list, it will be given a default value of [1].

TestNPARValues = [1, 2, 4, 8, 16];

# Values of NSIM to test.
# If set to None or an empty list, it will be given a default value of [4].

TestNSIMValues = [1, 2, 4, 8, 12, 16, 24, 32, 48, 64];

# Temporary directory to run VASP jobs.
# ** The script needs to overwrite the contents of this directory, and will therefore crash if it exists when it starts [better safe than sorry, right?] **

RunDir = "Tmp";

# Command to execute VASP.
# The string "<nproc>" must be present, and will be substituted with the number of MPI processes.

VASPRunCommand = "mpirun -np <nproc> ~/scratch/VASP/vasp.5.4.1.gpu/bin/vasp_gam";

# Name of archive directories to store completed jobs.
# The strings "<nproc>", "<kpar>", "<npar>" and "<nsim>", if present, will be substituted with the number of MPI processes, KPAR, NPAR and NSIM, respectively.
# The strings corresponding to the parameters being swept must be present.

ArchiveDirName = "CPUTest-<nproc>-<kpar>-<npar>-<nsim>";

# If True, skip running tests and collect results from any archive directories found.

CollectOnly = False;

# Path to the data output file.
# ** As the script would overwrite this file, it will crash if it already exists when it starts [again, better safe than sorry...] **

DataOutputFile = "CPUTest.csv";

# If larger than zero, the first N SCF steps will be ignored when computing the average SCF time.
# Useful for benchmarking e.g. ALGO = Fast or hybrids, where the first five SCF steps (typically) are very different to the others.

SkipSCFCycles = 5;


import commands;
import csv;
import os;

import shutil;

from Shared import CollectResults;


def _GetArchiveDirName(template, nproc, kpar, npar, nsim):
    jobDir = template;
    
    for find, replace in ("<nproc>", nproc), ("<kpar>", kpar), ("<npar>", npar), ("<nsim>", nsim):
        jobDir = jobDir.replace(find, str(replace));
    
    return jobDir;


if __name__ == "__main__":
    # Decide which parallelisation parameters are being swept, and set default values for KPAR, NPAR and NSIM if need be.

    if TestKPARValues == None or len(TestKPARValues) == 0:
        TestKPARValues = [1];
    
    if TestNPARValues == None or len(TestNPARValues) == 0:
        TestNPARValues = [1];
    
    if TestNSIMValues == None or len(TestNSIMValues) == 0:
        TestNSIMValues = [4];
    
    testKPAR = len(TestKPARValues) > 1;
    testNPAR = len(TestNPARValues) > 1;
    testNSIM = len(TestNSIMValues) > 1;

    # Startup checks.
    
    # If none of KPAR, NPAR or NSIM are being swept, the "test" may as well be run as a single VASP job, and it is quite likely a user error -> crash.
    
    if not (testKPAR or testNPAR or testNSIM):
        raise Exception("Error: One of TargetKPARValues, TargetNPARValues or TargetNSIMValues must be not be None and must contain more than one element.");
    
    # ArchiveDirName is required regardless of CollectOnly.
    
    for parameter, placeholder, required in ("KPAR", "<kpar>", testKPAR), ("NPAR", "<npar>", testNPAR), ("NSIM", "<nsim>", testNSIM):
        if required and placeholder not in ArchiveDirName:
            raise Exception("Error: If {0} is being tested, the string \"{1}\" must appear in ArchiveDirName.".format(parameter, placeholder));
    
    # DataOutputFile must not exist regardless of CollectOnly.
    
    if os.path.isfile(DataOutputFile):
        raise Exception("Error: DataOutputFile \"{0}\" already exists - please rename/delete and run again.".format(DataOutputFile));
    
    if not CollectOnly:
        # These other checks are only needed if CollectOnly is False.
    
        if os.path.isdir(RunDir):
            raise Exception("Error: RunDir \"{0}\" already exists - please remove and run again.".format(RunDir));
        
        if "<nproc>" not in VASPRunCommand:
            raise Exception("Error: The string \"<nproc>\" must appear in VASPRunCommand.");
        
        for vaspInputFile in "INCAR", "KPOINTS", "POSCAR", "POTCAR":
            if not os.path.isfile(vaspInputFile):
                raise Exception("Error: Required VASP input file \"{0}\" not found.".format(vaspInputFile));
        
        with open("INCAR", 'r') as inputReader:
            for line in inputReader:
                if "KPAR" in line or "NPAR" in line or "NSIM" in line:
                    raise Exception("Error: INCAR file must not contain the KPAR, NPAR or NSIM control tags - these are set by the script.");
    
    if not CollectOnly:
        for kparValue in TestKPARValues:
            for nparValue in TestNPARValues:
                # If the number of MPI processes is not divisible by KPAR * NPAR, VASP will almost certainly throw an error -> print a warning and skip this parameter combination.
                
                if NumProcesses % (kparValue * nparValue) != 0:
                    print("# proc = {0} is not divisible by KPAR * NPAR = {1} -> skipping...".format(NumProcesses, kparValue * nparValue));
                    print("");
                    
                    continue;
                
                for nsimValue in TestNSIMValues:
                    jobDir = _GetArchiveDirName(ArchiveDirName, NumProcesses, kparValue, nparValue, nsimValue);
            
                    if os.path.exists(jobDir):
                        print("Job dir \"{0}\" (# proc = {1}, KPAR = {2}, NPAR = {3}, NSIM = {4}) already exists -> skipping...".format(jobDir, NumProcesses, kparValue, nparValue, nsimValue));
                        print("");
                        
                        continue;
                    
                    os.mkdir(RunDir);
                    
                    os.chdir(RunDir);
                    
                    with open("INCAR", 'w') as outputWriter:
                        with open("../INCAR", 'r') as inputReader:
                            for line in inputReader:
                                outputWriter.write(line);
                        
                        outputWriter.write("\n");            
                        
                        outputWriter.write("! Parameters automatically added by CPUTest.py.\n");
                        outputWriter.write("\n");
                        
                        outputWriter.write("KPAR = {0}\n".format(kparValue));
                        outputWriter.write("NPAR = {0}\n".format(nparValue));
                        outputWriter.write("NSIM = {0}\n".format(nsimValue));
                    
                    for vaspInputFile in "KPOINTS", "POSCAR", "POTCAR":
                        shutil.copy("../{0}".format(vaspInputFile), vaspInputFile);
                    
                    print("Running test with # proc = {0}, KPAR = {1}, NPAR = {2}, NSIM = {3}...".format(NumProcesses, kparValue, nparValue, nsimValue));
                    
                    status, output = commands.getstatusoutput(
                        VASPRunCommand.replace("<nproc>", str(NumProcesses))
                        );
                    
                    print("  -> Exit status: {0}".format(status));
                    
                    os.chdir("..");
                    
                    stdOutFile = "{0}.out".format(jobDir);
                    
                    print("  -> Writing std out to \"{0}\"".format(jobDir));
                    
                    with open(stdOutFile, 'w') as outputWriter:
                        outputWriter.write(output);
                    
                    if status == 0:
                        print("  -> Renaming run directory to \"{0}\"".format(jobDir));
                        os.rename(RunDir, jobDir);
                    else:
                        shutil.rmtree(RunDir);
                    
                    print("");
    
    print("Collecting results...");
    
    data = { };
    
    for kparValue in TestKPARValues:
        for nparValue in TestNPARValues:
            if NumProcesses % (kparValue * nparValue) == 0:
                for nsimValue in TestNSIMValues:
                    jobDir = _GetArchiveDirName(ArchiveDirName, NumProcesses, kparValue, nparValue, nsimValue);
                    
                    if os.path.isdir(jobDir):
                        numSCFSteps, tSCFAve, tElapsed, finalTotalEnergy = CollectResults(jobDir, outcarSkipSCFCycles = SkipSCFCycles);
                        
                        if numSCFSteps != None and tSCFAve != None and tElapsed != None and finalTotalEnergy != None:
                            print("  -> Collected data for # proc = {0}, KPAR = {1}, NPAR = {2}, NSIM = {3}".format(NumProcesses, kparValue, nparValue, nsimValue));
                            data[(NumProcesses, kparValue, nparValue, nsimValue)] = (numSCFSteps, tSCFAve, tElapsed, finalTotalEnergy);
                        else:
                            print("  -> Failed to collect data for # proc = {0}, KPAR = {1}, NPAR = {2}, NSIM = {3}".format(NumProcesses, kparValue, nparValue, nsimValue));
                    else:
                        print("  -> Archive dir \"{0}\" not found -> skipping # proc = {1}, KPAR = {2}, NPAR = {3}, NSIM = {4}".format(jobDir, NumProcesses, kparValue, nparValue, nsimValue));
    
    print("");
    
    if len(data) > 0:
        print("Writing data to \"{0}\"...".format(DataOutputFile));
        
        with open(DataOutputFile, 'w') as outputWriter:
            outputWriterCSV = csv.writer(outputWriter, delimiter = ',', quotechar = '\"', quoting = csv.QUOTE_ALL);
            
            outputWriterCSV.writerow(["# Proc", "KPAR", "NPAR", "NSIM", "# SCF Steps", "t_SCF,Ave [s]", "t_Elapsed [s]", "Final E_0 [eV]"]);
            
            for key in sorted(data.keys()):
                outputWriterCSV.writerow(key + data[key]);
    else:
        print("No data collected - please check the *.out files from VASP jobs");
