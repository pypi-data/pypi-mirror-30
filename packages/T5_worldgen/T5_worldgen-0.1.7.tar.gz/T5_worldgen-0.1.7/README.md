# T5_worldgen
Traveller 5 worldgen

Python modules to generate Traveller 5 world(s).

Current status: it will generate a basic UWP with high-level system data and display a tab-separated view of the world. Works with Python 2 (2.7.12 tested) and 3 (3.5.2 tested).

## Usage
Clone, change directory to repo, run Python

```
from T5_worldgen.system import System
syst = System()
syst.display()
'0000\t\tD651667-6\tNi Po\t{-3}\t(B50+3)\t[5339]\tB\tS\t\t602\t8\t\tG7 V'
named_system = System('Den of Villiany')
named_system.display()
'0000\tDen of Villiany\tE764787-1\tAg Ri\t{+0}\t(462+1)\t[4753]\tBC\t\t\t500\t5\t\tK6 V'
syst2 = System('Coruscant', '0405')
syst2.display()
'0405\tCoruscant\tE530698-4\tDe Ni Na Po\t{-3}\t(653+0)\t[7320]\tB\t\t\t101\t6\t\tG0 V K3 V'
```

## To do
- Make Python packages
- Add generation and display for sector and subsector 
- SEC output
- T5 column and tab output suitable for use with https://travellermap.com/
