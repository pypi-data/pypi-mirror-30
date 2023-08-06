import numpy as np
import matplotlib.pyplot as plt
import taft.data

plotsCounter = 0

def displayPlots( title = None ):
	global plotsCounter

	plt.legend( loc="best" )
	plt.xlabel('Date')
	plt.ylabel('Profit')
	if title is not None:
		plt.title( title )
	plt.grid()	
	plt.show()
	plotsCounter = 0
# end of def

# Testing regression model without retraining
def regressionModelProfit( model, data, title="", entryFunction=None, entryStd=None, flipOver=False,
	verbose=False, plot=False, plotsCombined=False, useTPSL=False, rates=None ):
	
	if entryStd is None:
		entryStd = 2.0
	
	if entryFunction is None:
		def entryFunction( profit, meanZ, stdZ ):
			threshold = meanZ + stdZ * entryStd
			absMeanZ = np.abs(meanZ)
			if profit > threshold and profit > absMeanZ:
				return 1
			elif profit < -threshold and profit < -absMeanZ:
				return -1
			return 0 	
	# end of if		

	z = model.predict( data['inputs'] )
	lenZ = len(z)
	meanZ = np.mean(z)
	stdZ = np.std(z)
	overallProfit = 0.0
	cumulativeProfit = np.zeros( shape=(lenZ,) )
	numTrades = 0
	prevTrade = 0
	for i in range(lenZ-1,-1,-1):
		res = entryFunction( z[i], meanZ, stdZ )
		if 	isinstance( res, int ):
			trade = res
			tp = np.abs( z[i] )
			sl = tp
		else:
			trade, tp, sl = res
		profit = 0.0
		if trade == 1:
			if useTPSL:
				profit = simulateTrade( data['rateIndexes'][i], rates, tp, sl, 1 )
			else:
				profit = data['profit'][i]
			if not flipOver:
				numTrades += 1
			elif prevTrade != 1:
				numTrades += 1
			prevTrade = 1
		elif trade == -1:
			if useTPSL:
				profit = simulateTrade( data['rateIndexes'][i], rates, tp, sl, -1 )
			else:
				profit = -data['profit'][i]
			if not flipOver:
				numTrades += 1
			elif prevTrade != -1:
				numTrades += 1
			prevTrade = -1
		else:
			if flipOver:
				if prevTrade == 1:
					profit = testProfit[i]
				elif prevTrade == -1:
					profit = -testProfit[i]

		overallProfit += profit
		if i == lenZ-1:
			cumulativeProfit[i] = profit
		else:
			cumulativeProfit[i] = cumulativeProfit[i+1] + profit

	if verbose:
		print "Profit = %g (out of %d trades)" % (overallProfit, numTrades)

	if plot:
		if plotsCombined:
			global plotsCounter
			plotsCounter += 1
			if title == "":
				title = "#" + str(plotsCounter)
			title = "%s $=%g (%d)" % (title, overallProfit, numTrades)
		plt.plot( data['dtm'], cumulativeProfit, label=title )
		if not plotsCombined:
			plt.show()

	return { 'numTrades': numTrades, 'meanZ':meanZ, 'stdZ':stdZ, 'cumulativeProfit':cumulativeProfit, 'overallProfit':overallProfit }
# end of def 


# Testing regression model with re-training
def regressionModelTest( model, data, trainHistory=100, repeatTrainAfter=10, title="", 
	entryFunction=None, entryStd=None, normalize=False, flipOver=False, verbose=False, plot=False, plotsCombined=False, 
	useTPSL=False, rates=None ):
	
	if entryStd is None:
		entryStd = 2.0
	
	if entryFunction is None: 
		def entryFunction( profit, meanZ, stdZ ):
			threshold = meanZ + stdZ * entryStd
			absMeanZ = np.abs(meanZ)
			if profit > threshold and profit > absMeanZ:
				return 1
			elif profit < -threshold and profit < -absMeanZ:
				return -1
			return 0 	
	# end of if		

	lenData = len( data['profit'] )
	overallProfit = 0.0
	cumulativeProfitIndex = lenData - trainHistory
	cumulativeProfit = np.zeros( shape=(cumulativeProfitIndex+1,) )
	cumulativeProfit[cumulativeProfitIndex] = 0.0
	cumulativeProfitDtm = []
	for i in range(cumulativeProfitIndex+1):
		cumulativeProfitDtm.append(None)
	cumulativeProfitDtm[cumulativeProfitIndex] = data['dtm'][cumulativeProfitIndex]
	cumulativeProfitIndex -= 1
	numTrades = 0
	prevTrade = 0

	firstTrain = lenData
	lastTrain = lenData - trainHistory
	lastTest = lastTrain - repeatTrainAfter

	while(True):
		if verbose:
			print "$=%g, training: %d-%d, testing: %d-%d" % (overallProfit, firstTrain, lastTrain, lastTrain-1, lastTest)
		trainInputs = data['inputs'][lastTrain:firstTrain]
		trainProfit = data['profit'][lastTrain:firstTrain]
		testInputs =  data['inputs'][lastTest:lastTrain]
		testProfit =  data['profit'][lastTest:lastTrain]

		if normalize:
			status = normalizeInputs( trainInputs, testInputs )
			if status is None:
				break

		model.fit( trainInputs, trainProfit )
		z = model.predict( testInputs )
		lenZ = len(z)
		meanZ = np.mean(z)
		stdZ = np.std(z)
		for i in range(lenZ-1,-1,-1):
			res = entryFunction( z[i], meanZ, stdZ )
			if 	isinstance( res, int ):
				trade = res
				tp = np.abs(z[i])
				sl = tp
			else:
				trade, tp, sl = res
			profit = 0.0
			if trade == 1:
				if useTPSL:
					profit = simulateTrade( data['rateIndexes'][i], rates, tp, sl, 1 )
				else:
					profit = testProfit[i]
				if not flipOver:
					numTrades += 1
				elif prevTrade != 1:
					numTrades += 1
				prevTrade = 1
			elif trade == -1:
				if useTPSL:
					profit = simulateTrade( data['rateIndexes'][i], rates, tp, sl, -1 )					
				else:
					profit = -testProfit[i]
				if not flipOver:
					numTrades += 1
				elif prevTrade != -1:
					numTrades += 1
				prevTrade = -1
			else:
				if flipOver:
					if prevTrade == 1:
						profit = testProfit[i]
					elif prevTrade == -1:
						profit = -testProfit[i]

			overallProfit += profit
			cumulativeProfit[cumulativeProfitIndex] = cumulativeProfit[cumulativeProfitIndex+1] + profit
			cumulativeProfitDtm[cumulativeProfitIndex] = data['dtm'][cumulativeProfitIndex]			
			cumulativeProfitIndex -= 1

		firstTrain = lastTest + trainHistory 
		lastTrain = lastTest
		if lastTrain == 0:
			break
		lastTest = lastTrain - repeatTrainAfter
		if lastTest < 0:
			lastTest = 0
	# end of while

	if verbose:
		print "Profit = %g (out of %d trades)" % (overallProfit, numTrades)

	if plot:
		if plotsCombined:
			global plotsCounter
			plotsCounter += 1
			if title == "":
				title = "#" + str(plotsCounter)
			title = "%s $=%g (%d)" % (title, overallProfit, numTrades)
		plt.plot( cumulativeProfitDtm, cumulativeProfit, label=title )
		if not plotsCombined:
			plt.show()

	return { 'numTrades': numTrades, 'meanZ':meanZ, 'stdZ':stdZ, 'cumulativeProfit':cumulativeProfit, 'overallProfit':overallProfit }
# end of def 


def normalizeInputs( train, test ):
	numFeatures = np.shape( train )[1]
	for i in range(numFeatures):
		lenX, meanX, stdX = taft.data.normalize( train[:,i] )
		if lenX is None:
			return None
		lenX, _, _ = taft.data.normalize( test[:,i], meanX=meanX, stdX=stdX )
		if lenX is None:
			return None
	return "Ok"
# end of def 


def simulateTrade( rateIndex, rates, takeProfit, stopLoss, dir ):
	rate0 = rates['op'][rateIndex]
	if dir == 1:
		upper = rate0 + takeProfit
		lower = rate0 - stopLoss
	else:
		upper = rate0 + stopLoss
		lower = rate0 - takeProfit
	for i in range( rateIndex,-1, -1 ):
		if not ( rates['hi'][i] < upper ):
			if dir == -1:
				return -stopLoss
			else:
				return takeProfit
		if not ( rates['lo'][i] > lower ):
			if dir == 1:
				return -stopLoss
			else:
				return takeProfit
	if dir == 1:
		return rates['cl'][0] - rate0
	else: 
		return rate0 - rates['cl'][0]
# end of def
