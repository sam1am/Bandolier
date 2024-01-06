Output of tree command:
```
|-- .summary_files
    |-- code_summary.md
    |-- compressed_code_summary.md
    |-- previous_selection.json
|-- index.html
|-- script.js
|-- styles.css

```

---

./index.html
```
<!DOCTYPE html>
<html>

<head>
    <title>Grid Layout</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
        crossorigin="anonymous">
    <link rel="stylesheet" href="styles.css">
</head>

<body>
    <div class="container">
        <div class="row" id="layout-grid">
            <!-- Grids will be generated here -->
        </div>
    </div>
    <script src="script.js"></script>
</body>

</html>```
---

./styles.css
```
.square {
    border-radius: 5px;
    background-color: lightgrey;
    width: 30px;
    height: 55px;
    margin: 5px;
}

.marked {
    background-color: turquoise;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(4, 1fr);
    gap: 4px;
    width: 100px;
    margin-bottom: 1rem;
}

.grid-label {
    text-align: center;
}```
---

./script.js
```
let layoutGrid = document.getElementById('layout-grid');

let data = [
    ['MOOO', '.'],
    ['LOOO', '<Space>'],
    ['LROO', '<Tab>'],
    ['LLOO', '<Backspace>'],
    ['ORRO', 'f'],
    ['OMRO', 'y'],
    ['OOMO', 'o'],
    ['ORMO', 'g'],
    ['OMLO', 't'],
    ['OOOR', '<Return>'],
    ['OROR', 'c'],
    ['OMOR', 'h'],
    ['OLOR', 'l'],
    ['OORR', 'a'],
    ['ORRR', 'e'],
    ['OOMR', 'n'],
    ['ORMR', 'k'],
    ['OMMR', 'r'],
    ['OLMR', 'x'],
    ['OOLR', 'u'],
    ['OROM', 'j'],
    ['OMOM', 'i'],
    ['OLOM', 'v'],
    ['OORM', 'p'],
    ['OOMM', 'b'],
    ['ORMM', 's'],
    ['OMMM', 'm'],
    ['OOLM', 'z'],
    ['OOOL', '<escape>'],
    ['OOML', 'q'],
    ['OOLL', 'd'],
    ['OLLL', 'w']
];

data.forEach(([markings, letter]) => {
    let newItem = document.createElement('div');
    newItem.className = 'col-lg-3 col-md-4 col-sm-6 p-2';
    
    let label = document.createElement('p');
    label.className = 'grid-label';
    label.innerText = letter;
    newItem.appendChild(label);

    let newGrid = document.createElement('div');
    newGrid.className = 'grid';
    newItem.appendChild(newGrid);
    
    
    for (let row = 0; row < 4; row++) { // For each row
     for(let col=0; col<3; col++){ // For each column
         let square = document.createElement('div');
         square.classList.add('square'); // Add 'square' as a common class for all cells

         switch (markings.charAt(row)) {
             case 'O': break;
             case 'L': if (col === 0) square.classList.add('marked'); break;
             case 'M': if (col === 1) square.classList.add('marked'); break;
             case 'R': if (col === 2) square.classList.add('marked'); break;
         }
         newGrid.appendChild(square);
     }
}


    
    layoutGrid.appendChild(newItem);
});```
---
