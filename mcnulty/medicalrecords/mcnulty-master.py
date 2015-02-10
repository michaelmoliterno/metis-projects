import sqlite3
import pandas as pd

print 'hello world'
print 'hello world2'


con = sqlite3.connect('compData.db')


test_patients = pd.read_sql("SELECT count(distinct(tp.patientguid)) from training_patient tp join training_diagnosis td \
		where tp.patientguid = td.patientguid  and td.ICD9Code like '%314.00%'", con)

training_patients = pd.read_sql("SELECT count(distinct(tp.patientguid)) from test_patient tp join test_diagnosis td \
		where tp.patientguid = td.patientguid  and td.ICD9Code like '%314.00%'", con)

print test_patients
print training_patients




