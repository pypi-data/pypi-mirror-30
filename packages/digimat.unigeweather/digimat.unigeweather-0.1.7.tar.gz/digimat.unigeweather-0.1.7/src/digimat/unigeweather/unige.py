from io import StringIO
from io import BytesIO
import zipfile
import csv
import requests
from datetime import datetime, timedelta
import sys
import traceback


# Simple Parser/extractor for weather unige data files
# http://www.unige.ch/energie/forel/energie/activites/meteo/data-num.html

class CommentedFile:
    def __init__(self, f, commentstring="#"):
        self.f = f
        self.commentstring = commentstring

    def __next__(self):
        line = next(self.f).strip()
        while line.startswith(self.commentstring) or not line:
            line = next(self.f).strip()
        return line

    def __iter__(self):
        return self


class UnigeWeatherData(object):
    def __init__(self, site):
        self._site=site
        self.raz()

    def __len__(self):
        return self.count()

    @property
    def headers(self):
        return self._headers

    def raz(self):
        self._headers=[]
        self._data={}
        self._yearLoaded=[]

    def computeIndexFromRow(self, year, row):
        raise NotImplementedError

    def computeDatetimeFromIndex(self, index):
        raise NotImplementedError

    def store(self, year, row):
        try:
            index=self.computeIndexFromRow(year, row)
            if index not in self._data:
                self._data[index]=row
            else:
                print("DUP:WARNING"*60)
                print(self._data[index])
                print(row)
        except:
            # traceback.print_exc(file=sys.stdout)
            pass

    def rootUrl(self):
        return 'http://www.cuepe.ch/html/meteo/data-zip/%s' % self._site

    def url(self, year, fext='zip'):
        raise NotImplementedError

    def count(self):
        return len(self._data)

    def load(self, year=0):
        try:
            if year<=0:
                year=datetime.now().year

            if year not in self._yearLoaded:
                self._yearLoaded.append(year)

                data=None
                try:
                    url=self.url(year, 'csv')
                    r=requests.get(url)
                    if r and r.status_code==200:
                        data=r.text
                        csvfile=CommentedFile(StringIO(data))
                except Exception as e:
                    # traceback.print_exc(file=sys.stdout)
                    pass

                if not data:
                    try:
                        url=self.url(year, 'zip')
                        r=requests.get(url)
                        if r and r.status_code==200:
                            data=r.content
                            zfile=zipfile.ZipFile(BytesIO(data))
                            csvfile=CommentedFile(StringIO(str(zfile.read(zfile.namelist()[0]))))
                    except Exception as e:
                        # traceback.print_exc(file=sys.stdout)
                        pass

                reader = csv.reader(csvfile)

                rcount=self.count()
                for row in reader:
                    rdata=[s.strip() for s in row]
                    if rdata:
                        if self._headers:
                            try:
                                # tweak allowing to stop parsing when month/year section is reached
                                if rdata[0] in ['month', 'year']:
                                    break
                                self.store(year, rdata)
                            except:
                                traceback.print_exc(file=sys.stdout)
                                pass
                        else:
                            h=[s.lower() for s in rdata]
                            if h[0]:
                                # prevent using ",,,,," empty lines
                                self._headers=h

                return self.count()-rcount
        except Exception as e:
            print(str(e))
            pass
        return 0

    def names(self):
        return self._headers

    def column(self, name):
        try:
            return self._headers.index(name.lower())
        except:
            pass

    def row(self, index):
        try:
            return self._data[index]
        except:
            pass

    def value(self, name, index, default=None):
        try:
            value=self.row(index)[self.column(name)]
            if value and value != 'n/a' and value[:3] != '-99':
                return value
        except:
            pass
        return default

    def fvalue(self, name, index, default=None):
        try:
            value=self.value(name, index, None)
            if value is not None:
                return float(value)
        except:
            pass
        return default

    def doy(self, year, month, day):
        try:
            dt=datetime(year, month, day)
            return dt.timetuple().tm_yday
        except:
            return -1

    def dt(self):
        raise NotImplementedError

    def range(self, dt1, dt2):
        indexes=[]
        try:
            dt=self.dt()
            if dt1>dt2:
                (dt1, dt2)=(dt2, dt1)
            while dt1<=dt2:
                indexes.append(self.computeIndexFromDatetime(dt1))
                dt1+=dt
        except:
            traceback.print_exc(file=sys.stdout)
            pass

        return indexes

    def recordsFromTo(self, name, dt1, dt2):
        values=[]
        year=dt1.year
        while year<=dt2.year:
            self.load(year)
            year+=1
        for index in self.range(dt1, dt2):
            stamp=self.computeDatetimeFromIndex(index)
            fvalue=self.fvalue(name, index)
            if stamp is not None and fvalue is not None:
                values.append((stamp, fvalue))
        return values

    def records(self, name):
        records=[]
        indexes=list(self._data.keys())

        for index in indexes:
            dt=self.computeDatetimeFromIndex(index)
            value=self.fvalue(name, index)
            if dt is not None and value is not None:
                records.append((dt, value))

        return records

    def valueAt(self, name, dt, autoload=True):
        try:
            if autoload:
                self.load(dt.year)
            return self.fvalue(name, self.computeIndexFromDatetime(dt))
        except:
            pass

    def ta(self, dt, autoload=True):
        return self.valueAt('ta', dt, autoload)

    def hr(self, dt, autoload=True):
        return self.valueAt('hr', dt, autoload)

    def pr(self, dt, autoload=True):
        return self.valueAt('pr', dt, autoload)

    def gh(self, dt, autoload=True):
        return self.valueAt('gh', dt, autoload)

    def min(self, name, dt1, dt2):
        values=[v[1] for v in self.recordsFromTo(name, dt1, dt2)]
        return min(values)

    def max(self, name, dt1, dt2):
        values=[v[1] for v in self.recordsFromTo(name, dt1, dt2)]
        return max(values)

    def mean(self, name, dt1, dt2):
        values=[v[1] for v in self.recordsFromTo(name, dt1, dt2)]
        if values:
            count=len(values)
            return sum(values)/count
        return None


class UnigeWeatherDailyData(UnigeWeatherData):
    def url(self, year, fext='zip'):
        return '%s/%d-day.%s' % (self.rootUrl(), year, fext)

    def computeIndex(self, year, doy):
        return '%d/%d' % (year, doy)

    def computeIndexFromDatetime(self, dt):
        tt=dt.timetuple()
        return self.computeIndex(tt.tm_year, tt.tm_yday)

    def computeIndexFromRow(self, year, row):
        return self.computeIndex(year, int(row[0]))

    def dt(self):
        return timedelta(days=1)

    def computeDatetimeFromIndex(self, index):
        try:
            (year, doy)=index.split('/')
            dt=datetime(int(year), 1, 1)+timedelta(days=int(doy)-1)
            return dt
        except:
            pass


class UnigeWeatherHourlyData(UnigeWeatherData):
    def url(self, year, fext='zip'):
        return '%s/%d-hour.%s' % (self.rootUrl(), year, fext)

    def computeIndex(self, year, doy, hour):
        return '%d/%d/%d' % (year, doy, hour)

    def computeIndexFromDatetime(self, dt):
        tt=dt.timetuple()
        return self.computeIndex(tt.tm_year, tt.tm_yday, tt.tm_hour)

    def computeIndexFromRow(self, year, row):
        return self.computeIndex(year, int(row[0]), int(row[2]))

    def dt(self):
        return timedelta(hours=1)

    def computeDatetimeFromIndex(self, index):
        try:
            (year, doy, hour)=index.split('/')
            dt=datetime(int(year), 1, 1, int(hour))+timedelta(days=int(doy)-1)
            return dt
        except:
            pass


if __name__ == '__main__':
    pass
