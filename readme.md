# Antares

Named after α Scorpii, the brightest object in the Scorpius constellation.

## Prototype

Antares currently requires a very specific format because instead of doing a proper SQL Parser I am instead manipulating strings. Most commands need to be on their own line and cannot be multi-line.

## Incorrect

Antares will fail to parse the multi-line select statement and output garbage.

```sql
Select Top 5 a,
       b,
	   c
From Systems.dbo.Example
```
## Correct

Antares will detect the presence of `Top` but the Select columns must be in a single line statement.

```sql
Select Top 5 a, b, c
From Systems.dbo.Example
```
