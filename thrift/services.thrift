namespace py tblService

service tableService
{
        list<string> take_seat(1:list<string> l);
        list<string> leave_seat(1:list<string> l);
        list<string> hunger(1:list<string> l);
        list<string> return_token(1:list<string> l);
}

