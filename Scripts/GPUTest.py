# GPUTest.py by J. M. Skelton


# Numbers of MPI processes to test.

TestNumProcesses = [1, 2, 4, 8, 12, 16];

# Values of NSIM to test.

TestNSIMValues = [1, 2, 4, 8, 12, 16, 24, 32, 48, 64];

# Temporary directory to run VASP jobs.
# ** The script needs to overwrite the contents of this directory, and will therefore crash if it exists when it starts [better safe than sorry, right?] **

RunDir = "Tmp";

# Target value(s) of KPAR.
# The script will use the largest KPAR possible, provided the number of MPI processes is an integer muptiple.

TargetKPARValues = [1, 2, 4];

# Command to execute VASP.
# The string "<nproc>" must be present, and will be substituted with the number of MPI processes.

VASPRunCommand = "mpirun -np <nproc> ~/scratch/VASP/vasp.5.4.1.gpu/bin/vasp_gpu";

# Name of archive directories to store completed jobs.
# The strings "<nproc>" and "<nsim>" must be present, and will be substituted with the number of MPI processes and the value of NSIM, respectively.
# Optionally, the strings "<kpar>" and "<npar>" may be present, and will be replaced by the values of KPAR and NPAR.

ArchiveDirName = "GPUTest-<nproc>-<nsim>";

# If True, abort the loop over values of NSIM for a given number of MPI processes the first time a non-zero exit code is encountered.

AbortNSIMLoopOnFirstFail = True;

# If True, skip running tests and collect results from any archive directories found.

CollectOnly = False;

# Path to the data output file.
# ** As the script would overwrite this file, it will crash if it already exists when it starts [again, better safe than sorry...] **

DataOutputFile = "GPUTest.csv";

# If larger than zero, the first N SCF steps will be ignored when computing the average SCF time.
# Useful for benchmarking e.g. ALGO = Fast or hybrids, where the first five SCF steps (typically) are very different to the others.

SkipSCFCycles = 5;


import commands;
import csv;
import os;

import shutil;

from Shared import CollectResults;


def _CalculateKPARAndNPAR(numProcesses, targetKPARValues):
    kparValue = 1;
    
    for targetKPAR in sorted(targetKPARValues)[::-1]:
        if numProcesses % targetKPAR == 0:
            kparValue = targetKPAR;
    
    return (kparValue, numProcesses // kparValue);

def _GetArchiveDirName(template, nproc, nsim, kpar, npar):
    jobDir = template;
    
    for find, replace in ("<nproc>", nproc), ("<nsim>", nsim), ("<kpar>", kpar), ("<npar>", npar):
        jobDir = jobDir.replace(find, str(replace));
    
    return jobDir;


if __name__ == "__main__":
    # Startup checks.
    
    # ArchiveDirName is required regardless of CollectOnly.
    
    if "<nproc>" not in ArchiveDirName or "<nsim>" not in ArchiveDirName:
        raise Exception("Error: The strings \"<nproc>\" and \"<nsim>\" must appear in ArchiveDirName.");
    
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
        for numProcesses in TestNumProcesses:
            kparValue, nparValue = _CalculateKPARAndNPAR(numProcesses, TargetKPARValues);
            
            for nsimValue in TestNSIMValues:
                jobDir = _GetArchiveDirName(ArchiveDirName, numProcesses, nsimValue, kparValue, nparValue);
        
                if os.path.exists(jobDir):
                    print("Job dir \"{0}\" (# proc = {1}, NSIM = {2}) already exists -> skipping...".format(jobDir, numProcesses, nsimValue));
                    print("");
                    
                    continue;
                
                os.mkdir(RunDir);
                
                os.chdir(RunDir);
                
                with open("INCAR", 'w') as outputWriter:
                    with open("../INCAR", 'r') as inputReader:
                        for line in inputReader:
                            outputWriter.write(line);
                    
                    outputWriter.write("\n");            
                    
                    outputWriter.write("! Parameters automatically added by GPUTest.py.\n");
                    outputWriter.write("\n");
                    
                    outputWriter.write("KPAR = {0}\n".format(kparValue));
                    outputWriter.write("NPAR = {0}\n".format(nparValue));
                    outputWriter.write("NSIM = {0}\n".format(nsimValue));
                
                for vaspInputFile in "KPOINTS", "POSCAR", "POTCAR":
                    shutil.copy("../{0}".format(vaspInputFile), vaspInputFile);
                
                print("Running test with # proc = {0}, NSIM = {1}...".format(numProcesses, nsimValue));
                
                status, output = commands.getstatusoutput(
                    VASPRunCommand.replace("<nproc>", str(numProcesses))
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
                    
                    if AbortNSIMLoopOnFirstFail:
                        break;
                
                print("");
    
    print("Collecting results...");
    
    data = { };
    
    for numProcesses in TestNumProcesses:
        kparValue, nparValue = _CalculateKPARAndNPAR(numProcesses, TargetKPARValues);
        
        for nsimValue in TestNSIMValues:
            jobDir = _GetArchiveDirName(ArchiveDirName, numProcesses, nsimValue, kparValue, nparValue);
            
            if os.path.isdir(jobDir):
                numSCFSteps, tSCFAve, tElapsed, finalTotalEnergy = CollectResults(jobDir, outcarSkipSCFCycles = SkipSCFCycles);
                
                if numSCFSteps != None and tSCFAve != None and tElapsed != None and finalTotalEnergy != None:
                    print("  -> Collected data for # proc = {0}, NSIM = {1}".format(numProcesses, nsimValue));
                    data[(numProcesses, nsimValue)] = (kparValue, nparValue, numSCFSteps, tSCFAve, tElapsed, finalTotalEnergy);
                else:
                    print("  -> Failed to collect data for # proc = {0}, NSIM = {1}".format(numProcesses, nsimValue));
            else:
                print("  -> Archive dir \"{0}\" not found -> skipping # proc = {1}, NSIM = {2}".format(jobDir, numProcesses, nsimValue));
    
    print("");
    
    if len(data) > 0:
        print("Writing data to \"{0}\"...".format(DataOutputFile));
        
        with open(DataOutputFile, 'w') as outputWriter:
            outputWriterCSV = csv.writer(outputWriter, delimiter = ',', quotechar = '\"', quoting = csv.QUOTE_ALL);
            
            outputWriterCSV.writerow(["# Proc", "NSIM", "KPAR", "NPAR", "# SCF Steps", "t_SCF,Ave [s]", "t_Elapsed [s]", "Final E_0 [eV]"]);
            
            for key in sorted(data.keys()):
                outputWriterCSV.writerow(key + data[key]);
            
            outputWriterCSV.writerow([]);
            
            for matrixHeader, matrixColumn in ("# SCF Steps", 2), ("t_SCF,Ave [s]", 3), ("t_Elapsed [s]", 4):
                outputWriterCSV.writerow(["Data: {0}".format(matrixHeader)]);
                outputWriterCSV.writerow([]);
                
                outputWriterCSV.writerow(["", "NSIM"]);
                outputWriterCSV.writerow(["# Proc"] + TestNSIMValues);
                
                for numProcesses in TestNumProcesses:
                    outputWriterCSV.writerow(
                        [numProcesses] + [
                            data[(numProcesses, nsimValue)][matrixColumn] if (numProcesses, nsimValue) in data else '-'
                                for nsimValue in TestNSIMValues
                                ]
                        );
                
                outputWriterCSV.writerow([]);
    else:
        print("No data collected - please check the *.out files from VASP jobs");
