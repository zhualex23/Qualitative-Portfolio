# Market data input

The source file `Data File.csv` was referenced by the project draft (on a local Windows drive), and was subsequently provided as `553.647 Data File Course Project -- CY SP2026.xlsx`. The workbook has one sheet with daily adjusted prices from 2008 onward; the local reproduction package includes the converted CSV.

Supply the original course-provided **daily adjusted ETF price** CSV, containing `Date`, `SPY`, `BND`, `BIL`, and all eleven sectors: `XLC`, `XLY`, `XLP`, `XLE`, `XLF`, `XLV`, `XLI`, `XLB`, `XLRE`, `XLU`, `XLK`.

The original also contained `IEF`, `IWM`, `LQD`, `QQQ`, `SHY`, `TIP`, `TLT`, `VGIT`, `VGLT`, and `VGSH`; they are optional because these four strategies do not require them. Earlier history, preferably from 2018 or before, is needed for rolling estimation. In the draft, the full data starts in 2008, with some ETF columns missing before their inception.

Do not replace historical adjusted prices with current unadjusted closes: results will not match the original work.

**Data sharing:** `.gitignore` excludes `data/*.csv`. GitHub browser uploads do not enforce `.gitignore`, so do not manually upload `Data File.csv` into a public repository unless you have redistribution permission.
