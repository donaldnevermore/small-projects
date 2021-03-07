from urllib.request import urlopen

URL = "https://services.swpc.noaa.gov/json/solar-cycle/predicted-solar-cycle.json"
file = open("predicted-solar-cycle.json", "w")

for line in urlopen(URL).readlines():
    line = line.decode()
    file.write(line)

file.close()
