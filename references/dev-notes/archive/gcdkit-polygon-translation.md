# GCDkit R → IgneousWR JSON Polygon Translation

## GCDkit's `lines` Format

GCDkit stores polygon boundaries as individual `linesN` entries in R lists. Each entry uses x/y vectors:

```r
linesN=list("lines", x=c(x1,x2,x3,x4), y=c(y1,y2,y3,y4), col=plt.col[2])
```

Each `linesN` draws ONE edge set — GCDkit splits a zone across multiple `linesN` entries when edges are shared.

## Translation Process

### 1. Identify complete polygons

Multiple `linesN` entries connected by shared vertices form one classification zone. For JSON storage we store each zone as its own closed polygon, even with edge overlap.

### 2. Map clssf table

The `clssf` param maps index→name:
```r
clssf=list("NULL", use=2:19, rcname=c(
  "foidite","picrobasalt","basalt","basaltic andesite","andesite",
  "dacite","rhyolite","trachybasalt","basaltic trachyandesite",
  "trachyandesite","trachydacite","trachyte","tephrite",
  "phonotephrite","tephriphonolite","phonolite",
  "sodalitite/nephelinolith/leucitolith","silexite"
))
```

### 3. Polygon construction

Simple rectangle (Basalt/Bs):
```r
lines3=list("lines", x=c(45,52,52,45), y=c(0,0,5,5))
```
→ `[[45,0],[52,0],[52,5],[45,5]]`

Triangle (Trachybasalt/S1):
```r
lines8=list("lines", x=c(45,52,49.4), y=c(5,5,7.3))
```
→ `[[45,5],[52,5],[49.4,7.3]]`

### 4. Foidite — special case

Lines1 traces the outer envelope: bottom-left → Tephrite chain → top → top-right → top-left → back. Store as the full outer envelope. Overlapping inner polygons (Tephrite→Phonolite chain) draw on top so boundaries are correct visually.

### 5. Text-only zones

Some zones have no visual boundary:
```r
text15=list("text", x=55, y=18.5, text="Sodalitite/Nephelinolith/Leucitolith")
```

Store in `text_only` dict in JSON:
```json
"text_only": {
  "Sodalitite/Nephelinolith/Leucitolith": [55.0, 18.5],
  "Silexite": [85.0, 1.0]
}
```

### 6. IGWR key assignments

| GCDkit name | IGWR key | Notes |
|-------------|----------|-------|
| picrobasalt | Pc | |
| basalt | Bs | |
| basaltic andesite | O1 | |
| andesite | O2 | |
| dacite | O3 | |
| rhyolite | R | |
| trachybasalt | S1 | |
| basaltic trachyandesite | S2 | |
| trachyandesite | S3 | |
| trachydacite | Td | GCDkit-specific split |
| trachyte | T | Not Q%-split like Le Bas |
| tephrite | U1 | |
| phonotephrite | U2 | |
| tephriphonolite | U3 | |
| phonolite | Ph | |
| foidite | F | Largest polygon |
