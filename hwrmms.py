#!/usr/bin/env python3
# HWRM Map Scaler by SSSS

import re
import sys

# Note `ru-distance` sets the minimum distance RUs can be from each other
# This prevents RU deposits from clipping into each other
if len(sys.argv) not in (4, 5):
	print('HWRM Map Scaler By SSSS v1.0')
	print('  Scale up, or scale down multiplayer maps')
	print('  USAGE: {scriptName} <map-in> <map-out> <scale> [ru-distance=300]'
	      .format(scriptName=sys.argv[0]))
	sys.exit(1)

inPath = sys.argv[1]
outPath = sys.argv[2]
scale = float(sys.argv[3])
ruDist = float(sys.argv[4]) if len(sys.argv) > 4 else 300

coordFuncs0 = ('addPoint', 'addAsteroid', 'addDustCloud', 'addNebula', 'addPebble')
coordFuncs1 = ('setWorldBoundsInner', 'setWorldBoundsOuter')
coordfuncs = coordFuncs0 + coordFuncs1

radiusfuncs = ('addDustCloud', 'addNebula')

# The radii of each size of RU
# This is used in conjunction with `ru-distance`
asteroidRadii = [20, 50, 200]

mapHeader = '''-- Scaled with SSSS's Map Scaler
-- Scale Factor: {scale}
-- Minimum RU Spacing: {ruDist}

'''.format(scale=scale, ruDist=ruDist)

# Read map
with open(inPath, 'r') as f:
	oldMap = f.readlines()
	newMap = mapHeader

# Scale map
rus = []
for line in oldMap:
	func = line.strip().split('(')
	if func:
		func = func[0]
		
		# Scale down coordinate
		if func in coordfuncs:
			index = 1 if func in coordFuncs1 else 0
			coord = re.findall('{.*?}', line)[index]
			newCoord = re.sub(r'{|}|\s', r'', coord).split(',')
			newCoord = tuple(float(s) * scale for s in newCoord)
			
			# Spacing out asteroids (otherwise they spawn too close and collectors get stuck)
			if func == 'addAsteroid':
				l = line.lower()
				radius = asteroidRadii[0] if 'asteroid_3' in l or 'asteroid3_mp' in l else asteroidRadii[1] if 'asteroid_4' in l or 'asteroid4_mp' in l else asteroidRadii[2]
				repeat = True
				while repeat:
					for ruCoord, ruRadius in rus:
						dist = (sum((newCoord[i] - ruCoord[i])**2 for i in range(3)))**0.5
						if dist < (ruDist + radius + ruRadius):
							newCoord = tuple(newCoord[i] + (newCoord[i] - ruCoord[i]) * (ruDist + radius + ruRadius) / dist for i in range(3))
							break # Repeat the process
					else:	
						repeat = False
			
				rus.append((newCoord, radius))

			line = re.sub(coord, r'{%f, %f, %f}' % newCoord, line, count=1)
				
		# Scale down radii
		if func in radiusfuncs:
			radius = re.findall(r'\d+(?:\.\d+)?\s*(?=\))', line)[0]
			radiusNew = str(float(radius) * scale)
			line = re.sub(r'\d+(?:\.\d+)?\s*(?=\))', radiusNew, line)
		
	newMap += line

# Write map
with open(outPath, 'w') as f:
	f.write(newMap)
	
# Quit
print('Map successfully scaled')	
sys.exit(0)
