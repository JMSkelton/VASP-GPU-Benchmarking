# Shared.py by J. M. Skelton


import os;
import re;


_OUTCAR_TSCFRegex = re.compile("LOOP\:\s+cpu time\s+\d+\.\d+\:\s+real time\s+(?P<t_scf>\d+\.\d+)");
_OUTCAR_TElapsedRegex = re.compile("Elapsed time \(sec\)\:\s+(?P<t_elapsed>\d+\.\d+)");

_OSZICAR_TotalEnergyRegex = re.compile("E0= (?P<total_energy>[+-]?\d*\.\d+E[+-]?\d+)");


def ParseOUTCAR(filePath, skipSCFCycles = 0):
    numSCFSteps, tSCFAve, tElapsed = None, None, None;
    
    scfTimes = [];
    
    with open(filePath, 'r') as inputReader:
        for line in inputReader:
            match = _OUTCAR_TSCFRegex.search(line);
            
            if match:
                scfTimes.append(
                    float(match.group('t_scf'))
                    );
            else:
                match = _OUTCAR_TElapsedRegex.search(line);
                
                if match:
                    tElapsed = float(match.group('t_elapsed'));

    if skipSCFCycles > 0:
        if len(scfTimes) > skipSCFCycles:
            scfTimes = scfTimes[skipSCFCycles:];
        else:
            print("WARNING: _ParseOUTCAR(): Number of SCF steps {0} <= skipSCFCycles {1}".format(len(scfTimes), skipSCFCycles));
            scfTimes = [];
    
    if len(scfTimes) > 0:                        
        numSCFSteps = len(scfTimes);
        tSCFAve = sum(scfTimes) / numSCFSteps;
    
    return (numSCFSteps, tSCFAve, tElapsed);

def ParseOSZICAR(filePath):
    finalTotalEnergy = None;
    
    with open(filePath, 'r') as inputReader:
        for line in inputReader:
            match = _OSZICAR_TotalEnergyRegex.search(line);
            
            if match:
                finalTotalEnergy = float(match.group('total_energy'));
    
    return finalTotalEnergy;

def CollectResults(vaspDirectory, outcarSkipSCFCycles = 0):
    numSCFSteps, tSCFAve, tElapsed = None, None, None;
    
    outcarPath = os.path.join(vaspDirectory, "OUTCAR");
    
    if os.path.isfile(outcarPath):
        numSCFSteps, tSCFAve, tElapsed = ParseOUTCAR(outcarPath, skipSCFCycles = outcarSkipSCFCycles);
    else:
        print("WARNING: _CollectResults(): \"{0}\" not found".format(outcarPath));
    
    finalTotalEnergy = None;
    
    oszicarPath = os.path.join(vaspDirectory, "OSZICAR");
    
    if os.path.isfile(oszicarPath):
        finalTotalEnergy = ParseOSZICAR(oszicarPath);
    else:
        print("WARNING: _CollectResults(): \"{0}\" not found".format(oszicarPath));
    
    return (numSCFSteps, tSCFAve, tElapsed, finalTotalEnergy);
