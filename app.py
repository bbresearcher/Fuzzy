import sqlite3
import subprocess
from flask import Flask, render_template,request,flash

app=Flask(__name__)
app.config['SECRET_KEY'] = 'aZfe285BnpXvcz'

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

def delTest(id):
	retVal = True
	try:
		conn = get_db_connection()
		tests = conn.execute('DELETE from tests where id=?',(id,))
		conn.commit()
		tests = conn.execute('DELETE from test_data where test_id=?',(id,))
		conn.commit()
		conn.close()
		print("Test " +str(id) + " deleted")
		retVal = True
	except Exception as ex:
		print("Test " +str(id) + " NOT deleted")
		print(ex)
		retVal = False
	return retVal

    		
@app.route('/')
def fuzzy():
	isDBinit = checkDB()
	tmptests = getTests()
	return render_template('index.html',tests=tmptests)

@app.route('/addtest', methods=('GET', 'POST'))
def createTest():
	respMsg = ''
	if request.method == 'POST':
		testname = request.form['tname']
		nodepath = request.form['npath']
		circompath = request.form['cpath']
		rustpath = request.form['rpath']
		wasinserted = addTest(testname,nodepath,circompath,rustpath)
		if wasinserted:
			flash('Test created successfully')
		else:
			flash('Failed to create Test')

		return render_template('createTest.html')
	if request.method == 'GET':
		return render_template('createTest.html')
	
@app.route('/<int:idd>/edittest', methods=('GET', 'POST'))
def editTest(idd):
	respMsg = ''
	if request.method == 'POST':
		id = idd
		testname = request.form['tname']
		nodepath = request.form['npath']
		circompath = request.form['cpath']
		rustpath = request.form['rpath']
		wasinserted = updateTest(testname,nodepath,circompath,rustpath,id)
		if wasinserted:
			flash('Test updated successfully')
		else:
			flash('Failed to update Test')
		test = getTest(idd)
		
		return render_template('editTest.html',test=test)
	if request.method == 'GET':
		test = getTest(idd)
		return render_template('editTest.html',test=test)
	
@app.route('/<int:idd>/deletetest', methods=('GET', 'POST'))
def deleteTest(idd):
	respMsg = ''
	if request.method == 'POST':
		id = idd
		wasinserted = delTest(idd)
		if wasinserted:
			respMsg = 'Test updated successfully'
		else:
			respMsg = 'Failed to update Test'
		
		return respMsg
	if request.method == 'GET':
		tmptests = getTests()
		return render_template('index.html',tests=tmptests)
	
@app.route('/<int:idd>/edittestdata', methods=('GET', 'POST'))
def editTestData(idd):
	respMsg = ''
	if request.method == 'POST':
		id = idd
		f1data = request.form['f1data']
		f2data = request.form['f2data']
		expectedOutcome = request.form['expectedoutcome']
		wasinserted = updateTestData(f1data,f2data,expectedOutcome,idd)
		if wasinserted:
			respMsg = 'Test updated successfully'
		else:
			respMsg = 'Failed to update Test'		
		tmptestData = getaTestData(idd)
		return render_template('editTestData.html',testData=tmptestData)
	if request.method == 'GET':
		tmptestData = getaTestData(idd)
		return render_template('editTestData.html',testData=tmptestData)
	
@app.route('/<int:idd>/runtest', methods=('GET', 'POST'))
def runTest(idd):
	respMsg = ''
	if request.method == 'GET':
		id = idd
		testtorun = getTest(id)
		testname = testtorun['testname']
		nodepath = testtorun['nodepath']
		circompath = testtorun['circompath']
		rustpath = testtorun['rustpath']
		tmptestData = getTestData(idd)
		runId = createRun(id,testname + " test run")
		
		for row in tmptestData:
			nodeCommand = "node " + nodepath + " '" + row['field1_data'] + "' '" + row['field2_data'] + "' " + circompath
			rustCommand = "cd " + rustpath + " && cargo run -q -- '" + row['field1_data'] + "' '" + row['field2_data'] + "'"
			circomResp = subprocess.check_output(nodeCommand,shell=True)
			rustResp = subprocess.check_output(rustCommand,shell=True)
			castCommand = "cast --to-base " + str(rustResp.decode()[1:67]) + " 10"
			castResp  = subprocess.check_output(castCommand,shell=True)
			circomMatch = 0
			rustMatch = 0
			wereEqual = 0
			cout = circomResp.decode()[0:len(circomResp.decode())-1]
			rout = castResp.decode()[0:len(castResp.decode())-1]
			if cout == rout:
				wereEqual = 1
			print("Expected outcome: ")
			print(row['expected_output'])
			if cout == row['expected_output']:
				circomMatch = 1
			if rout == row['expected_output']:
				rustMatch = 1

			wasinserted = insertTestData(runId,cout,circomMatch,rout,rustMatch,wereEqual)

		testOutcomes = getOutcomes(runId)
		runVals = getRun(runId)
		createdDate = runVals['created']
		descr = runVals['rundescription']
		tmpruns = getAllRuns()
	return render_template('runTest.html',testOutcomes=testOutcomes,runs=tmpruns,createdDate=createdDate,descr=descr)

@app.route('/<int:idd>/viewruns', methods=('GET', 'POST'))
def viewRun(idd):
	respMsg = ''
	if request.method == 'GET':
		try:
			id = idd
			testOutcomes = getOutcomes(id)
			runVals = getRun(int(testOutcomes[0]['run_id']))
			createdDate = runVals['created']
			descr = runVals['rundescription']
			tmpruns = getAllRuns()
		except:
			print("Failed to retrieve any tests")
			tmpruns = getAllRuns()
			return render_template('runTest.html',runs=tmpruns)
	return render_template('runTest.html',testOutcomes=testOutcomes,runs=tmpruns,createdDate=createdDate,descr=descr)

@app.route('/runsql', methods=('GET', 'POST'))
def runSQL():
	respMsg = ''
	wasinserted = False
	if request.method == 'POST':
		SQLscript = request.form['sql']
		if SQLscript != "":
			wasinserted = runScript(SQLscript)
		if wasinserted:
			flash('Script ran successfully')
		else:
			flash('Script Failed to run')

		return render_template('runscript.html',respMsg=respMsg)
	if request.method == 'GET':
		return render_template('runscript.html',respMsg=respMsg)


if  __name__ == "__main__":
	
	app.run()
