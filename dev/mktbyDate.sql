
declare @t datetime

select @t = max(TradeDate) from stocks..tblTradeDates where TradeDate < dateadd(yy, @y, getdate())

print @t

select top 100 Symbol, TradeDate, MarketCap from stocks..tblStockHistory
where TradeDate = @t
and MarketCap is not NULL AND MarketCap != 0
order by TradeDate, MarketCap desc
