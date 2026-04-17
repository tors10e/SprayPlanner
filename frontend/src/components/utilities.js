

// Look at each event in the events file and make a new list with
// those that are not in the past.


export function GetDayOfTheWeek(day_of_week) {
    const weekday = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    return weekday[day_of_week];
}

export function StringToDayOfTheWeek(date_string) {
    var date_value = new Date(date_string);
    var day_number = date_value.getDay();
    return GetDayOfTheWeek(day_number);
}

export function MakeDateNiceToRead(orginal_date) {
    var pretty_date = new Date(orginal_date);
    pretty_date = pretty_date.toLocaleDateString('en-us', { weekday:"short", month:"short", day:"numeric"})
    return pretty_date;
    }