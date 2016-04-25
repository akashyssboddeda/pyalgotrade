from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.tools import yahoofinance
from pyalgotrade.technical import bollinger
from pyalgotrade.stratanalyzer import sharpe
import csv

class BBands(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, bBandsPeriod):
        strategy.BacktestingStrategy.__init__(self, feed, 50000)
        self.__instrument = instrument
        self.__bbands = bollinger.BollingerBands(feed[instrument].getCloseDataSeries(), bBandsPeriod, 2)

    def getBollingerBands(self):
        return self.__bbands

    def onBars(self, bars):
        lower = self.__bbands.getLowerBand()[-1]
        upper = self.__bbands.getUpperBand()[-1]
        if lower is None:
            return

        shares = self.getBroker().getShares(self.__instrument)
        bar = bars[self.__instrument]
        if shares == 0 and bar.getClose() < lower:
            sharesToBuy = int(self.getBroker().getCash(False) / bar.getClose())
            self.marketOrder(self.__instrument, sharesToBuy)
        elif shares > 0 and bar.getClose() > upper:
            self.marketOrder(self.__instrument, -1*shares)


def main(plot):
    symbol_file = open("TFEX","r")
    #Read each symbol and remove \n from each symbol
    symbols = [x.strip('\n') for x in symbol_file.readlines()]

    #symbols = ["aot.bk","bbl.bk","tpipl.bk","ichi.bk"]
    bBandsPeriod = 21

    f = open("bbands_result.txt","w")
    # Download the bars.
    for instrument in symbols:
	instrument = instrument+".BK"
    	feed = yahoofinance.build_feed([instrument], 2015, 2016, ".")

    	strat = BBands(feed, instrument, bBandsPeriod)
    	sharpeRatioAnalyzer = sharpe.SharpeRatio()
    	strat.attachAnalyzer(sharpeRatioAnalyzer)

    	if plot:
        	plt = plotter.StrategyPlotter(strat, True, True, True)
        	plt.getInstrumentSubplot(instrument).addDataSeries("upper", strat.getBollingerBands().getUpperBand())
        	plt.getInstrumentSubplot(instrument).addDataSeries("middle", strat.getBollingerBands().getMiddleBand())
        	plt.getInstrumentSubplot(instrument).addDataSeries("lower", strat.getBollingerBands().getLowerBand())

    	strat.run()
	print "%s" % instrument
    	print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.03)
	f.write("%s\n" % instrument)
	f.write("Sharpe ratio: %.2f\n" % sharpeRatioAnalyzer.getSharpeRatio(0.03))
    	if plot:
        	plt.plot()


if __name__ == "__main__":
    main(False)
