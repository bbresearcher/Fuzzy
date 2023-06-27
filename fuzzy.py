import sqlite3
import subprocess
import random
from flask import Flask, render_template,request

app=Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
    
def checkDB():
	try:
		conn = get_db_connection()
		isinit = conn.execute('SELECT * from is_init').fetchall()
		conn.close()
	except:
		with open('schema.sql') as f:
			conn.executescript(f.read())
		conn.close()
		isinit = 0
	return isinit

def runScript(sql):
	scriptRan = False
	try:
		conn = get_db_connection()
		conn.executescript(sql)
		conn.close()
		scriptRan = True
	except:
		scriptRan = False
	return scriptRan

def getTests():
	conn = get_db_connection()
	tests = conn.execute('SELECT * FROM tests').fetchall()
	conn.close()
	return tests

def getAllRuns():
	conn = get_db_connection()
	tests = conn.execute('SELECT * FROM test_runs').fetchall()
	conn.close()
	return tests

def getRun(id):
	conn = get_db_connection()
	tests = conn.execute('SELECT * FROM test_runs where id=' + str(id)).fetchone()
	conn.close()
	return tests

def getTest(id):
	conn = get_db_connection()
	tests = conn.execute('SELECT * FROM tests where id=' + str(id)).fetchone()
	conn.close()
	return tests

def getTestData(idd):
	conn = get_db_connection()
	tests = conn.execute('SELECT * FROM test_data where test_id=' + str(idd)).fetchall()
	conn.close()
	return tests

def getaTestData(idd):
	conn = get_db_connection()
	tests = conn.execute('SELECT * FROM test_data where test_id=' + str(idd)).fetchone()
	conn.close()
	return tests


def addTest(testname,npath,cpath,rpath):
	retVal = True
	try:
		conn = get_db_connection()
		cursor=conn.cursor()
		tests = cursor.execute('INSERT INTO tests (testname,nodepath,circompath,rustpath) VALUES (?,?,?,?)',(testname,npath,cpath,rpath))
		## crete test data record
		tests = conn.execute('INSERT INTO test_data (test_id,input_data,expected_output) VALUES (?,?,?)',(cursor.lastrowid,"",""))
		conn.commit()
		conn.close()
		retVal = True
	except Exception as ex:
		print(ex)
		retVal = False
	return retVal

def createRun(id,rundescription):
	retVal = 0
	try:
		conn = get_db_connection()
		cursor=conn.cursor()
		tests = cursor.execute('INSERT INTO test_runs (test_id,rundescription) VALUES (?,?)',(id,rundescription))
		retVal = cursor.lastrowid
		conn.commit()
		conn.close()
		
	except Exception as ex:
		print(ex)
		retVal = 0
	return retVal

def insertTestData(id,circomoutput,circomMatch,rustoutput,rustMatch,wereEqual):
	retVal = False
	try:
		conn = get_db_connection()
		cursor=conn.cursor()
		tests = cursor.execute('INSERT INTO test_outcomes (run_id,circomoutput,circommatch,rustoutput,rustmatch,wereEqual) VALUES (?,?,?,?,?,?)',(id,circomoutput,circomMatch,rustoutput,rustMatch,wereEqual))
		conn.commit()
		conn.close()
		retVal = True
	except Exception as ex:
		print(ex)
		retVal = False
	return retVal

def getOutcomes(idd):
	conn = get_db_connection()
	tests = conn.execute('SELECT * FROM test_outcomes where run_id=' + str(idd)).fetchall()
	conn.close()
	return tests

def updateTest(testname,npath,cpath,rpath,id):
	retVal = True
	try:
		conn = get_db_connection()
		tests = conn.execute('UPDATE tests set testname=?,nodepath=?,circompath=?,rustpath=? where id=?',(testname,npath,cpath,rpath,id))
		conn.commit()
		conn.close()
		retVal = True
	except:
		retVal = False
	return retVal

def updateTestData(f1data,f2data,expectOutput,id):
	retVal = True
	try:
		conn = get_db_connection()
		tests = conn.execute('UPDATE test_data set field1_data=?,field2_data=?,expected_output=? where tesT_id=?',(f1data,f2data,expectOutput,id))
		conn.commit()
		conn.close()
		retVal = True
	except:
		retVal = False
	return retVal

def generateInputField():
	fieldsize = int(round(random.uniform(1,78)))
	genfield = ""
	for i in range(fieldsize):
		genfield += str(round(random.uniform(0,9)))
	return genfield

def runFuzzer(test_id,number_of_fuzz_runs,add_results_to_db):
    id = int(test_id) 
    numRuns= int(number_of_fuzz_runs) 
    addtoDb = int(add_results_to_db) 
    testtorun = getTest(id) 
    testname = testtorun['testname']
    nodepath = testtorun['nodepath']
    circompath = testtorun['circompath']
    rustpath = testtorun['rustpath']
    runId = 0
    if addtoDb == 1:
        runId = createRun(id,testname + " test run")

    try:
        for i in range(numRuns):
            inputfield1 = generateInputField()
            inputfield2 = generateInputField()
            print("-----------------------------------------------------------------------")
            print("[+] Input 1           : ",inputfield1)
            print("[+] Input 2           : ",inputfield2)
            nodeCommand = "node " + nodepath + " '" + inputfield1 + "' '" + inputfield2 + "' " + circompath
            rustCommand = "cd " + rustpath + " && cargo run -q -- '" + inputfield1 + "' '" + inputfield2 + "'"
            circomResp = subprocess.check_output(nodeCommand,shell=True)
            rustResp = subprocess.check_output(rustCommand,shell=True)
            castCommand = "cast --to-base " + str(rustResp.decode()[1:67]) + " 10"
            castResp  = subprocess.check_output(castCommand,shell=True)
            circomMatch = 0
            rustMatch = 0
            wereEqual = 0
            cout = circomResp.decode()[0:len(circomResp.decode())-1]
            rout = castResp.decode()[0:len(castResp.decode())-1]
            print("[+] Circom output     : ",cout)
            print("[+] Rust output       : ",rout)
            if cout == rout:
                wereEqual = 1
            print("[+] Did outputs match : ",wereEqual)
            print("-----------------------------------------------------------------------")
            print("")
            if addtoDb == 1:
                wasinserted = insertTestData(runId,cout,circomMatch,rout,rustMatch,wereEqual)
	
    except Exception as e:
        print("Fuzz function exception : ",e)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("test_id", help="The test id in the Fuzzy database")
    parser.add_argument("number_of_fuzz_runs", help="The number of fuzz runs to try")
    parser.add_argument("add_results_to_db", help="The number of fuzz runs to try")
    args = parser.parse_args()
    runFuzzer(args.test_id,args.number_of_fuzz_runs,args.add_results_to_db)

main()
