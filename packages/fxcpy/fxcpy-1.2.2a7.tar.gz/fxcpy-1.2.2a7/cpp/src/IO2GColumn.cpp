#include "stdafx.h"
//#include <IO2GColumn.h>

using namespace boost::python;

class IO2GTableColumnWrap : public IO2GTableColumn, public wrapper < IO2GTableColumn >
{
public:
	const char* getID() { return this->get_override("getID")(); }
	O2GTableColumnType getType(){ return this->get_override("getType")(); }
};

class IO2GTableColumnCollectionWrap : public IO2GTableColumnCollection, public wrapper < IO2GTableColumnCollection >
{
public:
	int size() { return this->get_override("size")(); }
	IO2GTableColumn* get(int) { return this->get_override("get")(); }
	IO2GTableColumn* find(const char *){ return this->get_override("find")(); }
};

void export_IO2GColumn()
{
	object obj_IO2GTableColumn = class_<IO2GTableColumnWrap, bases<IAddRef>, boost::noncopyable>("IO2GTableColumn", no_init)
		.def("getID", pure_virtual(&IO2GTableColumn::getID))
		.def("getType", pure_virtual(&IO2GTableColumn::getType))
		;
	{
		scope in_IO2GTableColumn(obj_IO2GTableColumn);
		enum_<IO2GTableColumn::O2GTableColumnType>("IO2GTableColumnType")
			.value("Integer", IO2GTableColumn::Integer)
			.value("Double", IO2GTableColumn::Double)
			.value("String", IO2GTableColumn::String)
			.value("Date", IO2GTableColumn::Date)
			.value("Boolean", IO2GTableColumn::Boolean)
			.export_values()
			;

	}

	class_<IO2GTableColumnCollectionWrap, bases<IAddRef>, boost::noncopyable>("IO2GTableColumnCollection", no_init)
		//.def("__len__", &IO2GTableColumnCollection::size)
		//.def("__getitem__", &IO2GTableColumnCollection::get, return_value_policy<reference_existing_object>())
		.def("size", pure_virtual( &IO2GTableColumnCollection::size))
		.def("get", pure_virtual(&IO2GTableColumnCollection::get), return_value_policy<reference_existing_object>())
		.def("find", pure_virtual(&IO2GTableColumnCollection::find), return_value_policy<reference_existing_object>())
		;
}