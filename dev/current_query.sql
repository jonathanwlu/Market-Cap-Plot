select Symbol, MarketCap from stocks..tblStocks
where EndDate is NULL AND (MarketCap is not NULL AND MarketCap != 0) 
order by MarketCap desc
