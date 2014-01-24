from __init__ import OwrdWaterIO

wells = OwrdWaterIO(filename="owrd_wls.txt")
f = open('owrd_wells.csv', 'w+')
f.write(','.join(wells.field_names))
f.write('\n')
for well in wells:
    if (well.logid[:4] == 'KLAM'):
        f.write('"')
        f.write('","'.join(well))
        f.write('"')
        f.write('\n')
f.close()

redrills = OwrdWaterIO(filename="owrd_redrills.txt")
f = open('owrd_redrills.csv', 'w+')
f.write(','.join(redrills.field_names))
f.write('\n')
for red in redrills:
    if (red.logid[:4] == 'KLAM'):
        f.write('"')
        f.write('","'.join(red))
        f.write('"')
        f.write('\n')
f.close()

master = OwrdWaterIO(filename="owrd_master.txt")
f = open('owrd_master.csv', 'w+')
f.write(','.join(master.field_names))
f.write('\n')
for mast in master:
    if (mast.basin == 'KLAMATH'):
        f.write('"')
        f.write('","'.join(mast))
        f.write('"')
        f.write('\n')
f.close()

