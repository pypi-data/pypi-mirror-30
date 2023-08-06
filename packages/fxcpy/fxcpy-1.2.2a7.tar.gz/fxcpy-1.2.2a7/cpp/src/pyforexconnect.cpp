#include "stdafx.h"
#include "ForexConnectClient.h"

BOOST_PYTHON_MODULE(forexconnect)
{   
    Py_Initialize();
    PyEval_InitThreads();
    using namespace boost::python;

	//root
        export_IAddRefClass();
	export_IO2GColumn();
	export_IO2GLoginRules();
	export_IO2GPermissionChecker();
	export_IO2GRequest();
	export_IO2GResponse();
	export_IO2GRow();
	export_IO2GSession();
        
	//IO2GTable_Begin
	export_IO2GGenericTableResponseReader();
	export_IO2GOffersTableResponseReader();
	export_IO2GAccountsTableResponseReader();
	export_IO2GOrdersTableResponseReader();
	export_IO2GTradesTableResponseReader();
	export_IO2GClosedTradesTableResponseReader();
	export_IO2GMessagesTableResponseReader();
	export_IO2GTableIterator();
	export_IO2GTableListener();
	export_IO2GTable();
	export_IO2GTableManager();
	export_IO2GOffersTable();
	export_IO2GAccountsTable();
	export_IO2GOrdersTable();
	export_IO2GTradesTable();
	export_IO2GClosedTradesTable();
	export_IO2GMessagesTable();
	export_IO2GSummaryTable();
        
	//IO2GTable_End
	export_IO2GTimeframe();
	export_IO2GTradingSettingsProvider();
	export_O2GDateUtils();
	export_O2GEnum();
	export_O2GRequestParamsEnum();
	export_CO2GTransport();
        
	// enumerations exports
	export_AccountsColumnsEnum();
	export_TradesColumnsEnum();
	export_ClosedTradesColumnsEnum();
	export_MessagesColumnsEnum();
	export_OffersColumnsEnum();
	export_OrdersColumnsEnum();
	export_SummariesColumnsEnum();
        
	// readers
	export_IO2GLastOrderUpdateResponseReader();
	export_IO2GMarketDataResponseReader();
	export_IO2GMarketDataSnapshotResponseReader();
	export_IO2GOrderResponseReader();
	export_IO2GSystemPropertiesReader();
	export_IO2GTablesUpdatesReader();
	export_IO2GTimeConverter();
        
	// rows
	export_IO2GAccountRow();
	export_IO2GClosedTradeRow();
	export_IO2GMessageRow(); 
	export_IO2GOfferRow();
	export_IO2GOrderRow();
	export_IO2GSummaryRow();
	export_IO2GTradeRow();
	export_O2G2PteredClasses();    
};
