const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const previewImage = document.getElementById('previewImage');
const uploadText = document.getElementById('uploadText');

const outputBox1Container = document.getElementById('outputBox1Container');
const outputImage1 = document.getElementById('outputImage1');
const outputBox2Container = document.getElementById('outputBox2Container');
const outputImage2 = document.getElementById('outputImage2');
const outputBox3Container = document.getElementById('outputBox3Container');
const outputImage3 = document.getElementById('outputImage3');
const outputBox4Container = document.getElementById('outputBox4Container');
const outputImage4 = document.getElementById('outputImage4');
const outputBox5Container = document.getElementById('outputBox5Container');
const outputImage5 = document.getElementById('outputImage5');
const outputBox6Container = document.getElementById('outputBox6Container');
const outputImage6 = document.getElementById('outputImage6');

const checkPortfolio = document.getElementById('checkPortfolio');
const checkOrder = document.getElementById('checkOrder');
const checkOrderO = document.getElementById('checkOrderO');
const checkOrderC = document.getElementById('checkOrderC');
const checkOrderOP = document.getElementById('checkOrderOP');
const checkOrderOC = document.getElementById('checkOrderOC');

const outputConfigs = [
    {
        key: 'portfolio',
        checkbox: checkPortfolio,
        container: outputBox1Container,
        image: outputImage1,
        loaderId: 'loader1',
        loaderText: 'Processing Portfolio...',
        fnName: 'process_portfolio_image'
    },
    {
        key: 'order',
        checkbox: checkOrder,
        container: outputBox2Container,
        image: outputImage2,
        loaderId: 'loader2',
        loaderText: 'Processing Order...',
        fnName: 'process_order_image'
    },
    {
        key: 'orderO',
        checkbox: checkOrderO,
        container: outputBox3Container,
        image: outputImage3,
        loaderId: 'loader3',
        loaderText: 'Processing Order O...',
        fnName: 'order_o'
    },
    {
        key: 'orderC',
        checkbox: checkOrderC,
        container: outputBox4Container,
        image: outputImage4,
        loaderId: 'loader4',
        loaderText: 'Processing Order C...',
        fnName: 'order_c'
    },
    {
        key: 'orderOP',
        checkbox: checkOrderOP,
        container: outputBox5Container,
        image: outputImage5,
        loaderId: 'loader5',
        loaderText: 'Processing Order OP...',
        fnName: 'order_op'
    },
    {
        key: 'orderOC',
        checkbox: checkOrderOC,
        container: outputBox6Container,
        image: outputImage6,
        loaderId: 'loader6',
        loaderText: 'Processing Order OC...',
        fnName: 'order_oc'
    }
];

let pyodide = null;
let pyodideLoadingPromise = null;
let lastImageBytes = null;
let lastResults = {};
let currentJobId = 0;

async function initPyodide() {
    if (!pyodide) {
        uploadText.textContent = 'Loading Python Environment...';
        pyodide = await loadPyodide();
        await pyodide.loadPackage(["numpy", "Pillow", "requests"]);

        const processCode = await (await fetch('process.py')).text();
        pyodide.runPython(processCode);

        const snippetNames = ["Snippet_Account.png", "Snippet_Closing_Partial.png", "Snippet_Closing.png", "Snippet_Opening_Partial.png", "Snippet_Opening.png"];
        for (const name of snippetNames) {
            const response = await fetch(name);
            const buffer = await response.arrayBuffer();
            pyodide.FS.writeFile(name, new Uint8Array(buffer));
        }

        uploadText.textContent = 'Python Ready. Upload Image.';
    }
    return pyodide;
}

pyodideLoadingPromise = initPyodide().catch(err => {
    console.error("Pyodide initialization failed:", err);
    uploadText.textContent = 'Error loading Python. Try refreshing.';
});

function clearLoader(config) {
    const loader = document.getElementById(config.loaderId);
    if (loader) {
        loader.remove();
    }
}

function setOutputHidden(config) {
    clearLoader(config);
    config.container.style.display = 'none';
    config.image.style.display = 'none';
}

function showLoader(config) {
    clearLoader(config);
    config.container.style.display = 'flex';
    config.image.style.display = 'none';
    config.container.insertAdjacentHTML('beforeend', `<p class="loader" id="${config.loaderId}">${config.loaderText}</p>`);
}

function showResult(config, result) {
    clearLoader(config);
    config.container.style.display = 'flex';
    config.image.src = 'data:image/png;base64,' + result;
    config.image.style.display = 'block';
}

function setLoaderError(config) {
    const loader = document.getElementById(config.loaderId);
    if (loader) {
        loader.textContent = 'Error';
    }
}

async function processConfigs(configs, jobId) {
    const activeConfigs = configs.filter(config => config.checkbox.checked);
    if (!activeConfigs.length || !lastImageBytes) {
        return;
    }
    await pyodideLoadingPromise;
    if (!pyodide) {
        throw new Error("Pyodide not initialized.");
    }

    const imageBytesPy = pyodide.toPy(new Uint8Array(lastImageBytes));
    const tasks = activeConfigs.map(async (config) => {
        const fn = pyodide.globals.get(config.fnName);
        const result = await fn(imageBytesPy);
        if (fn.destroy) {
            fn.destroy();
        }
        return { config, result };
    });

    const results = await Promise.all(tasks);
    if (imageBytesPy.destroy) {
        imageBytesPy.destroy();
    }
    if (jobId !== currentJobId) {
        return;
    }

    results.forEach(({ config, result }) => {
        lastResults[config.key] = result;
        if (config.checkbox.checked) {
            showResult(config, result);
        } else {
            setOutputHidden(config);
        }
    });
}

uploadBox.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (!file) {
        return;
    }

    uploadText.style.display = 'none';
    previewImage.src = URL.createObjectURL(file);
    previewImage.style.display = 'block';

    currentJobId += 1;
    const jobId = currentJobId;
    lastResults = {};
    lastImageBytes = null;

    outputConfigs.forEach((config) => {
        if (config.checkbox.checked) {
            showLoader(config);
        } else {
            setOutputHidden(config);
        }
    });

    try {
        const reader = new FileReader();
        reader.onload = async (e) => {
            lastImageBytes = e.target.result;
            const selectedConfigs = outputConfigs.filter(config => config.checkbox.checked);
            if (!selectedConfigs.length) {
                return;
            }
            try {
                await processConfigs(selectedConfigs, jobId);
            } catch (error) {
                console.error("Processing error:", error);
                selectedConfigs.forEach(setLoaderError);
            }
        };
        reader.readAsArrayBuffer(file);
    } catch (error) {
        console.error("Processing error:", error);
        uploadText.textContent = 'Error processing image.';
        uploadText.style.display = 'block';
        previewImage.style.display = 'none';
        outputConfigs.forEach(setLoaderError);
    }
});

outputConfigs.forEach((config) => {
    config.checkbox.addEventListener('change', async () => {
        if (!config.checkbox.checked) {
            setOutputHidden(config);
            return;
        }
        if (!lastImageBytes) {
            setOutputHidden(config);
            return;
        }
        if (lastResults[config.key]) {
            showResult(config, lastResults[config.key]);
            return;
        }
        const jobId = currentJobId;
        showLoader(config);
        try {
            await processConfigs([config], jobId);
        } catch (error) {
            console.error("Processing error:", error);
            setLoaderError(config);
        }
    });
});
