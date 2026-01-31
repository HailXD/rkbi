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
const outputBox7Container = document.getElementById('outputBox7Container');
const outputImage7 = document.getElementById('outputImage7');

const outputSelect = document.getElementById('outputSelect');

const outputConfigs = [
    {
        key: 'portfolio',
        container: outputBox1Container,
        image: outputImage1,
        loaderId: 'loader1',
        loaderText: 'Processing Portfolio...',
        fnName: 'process_portfolio_image'
    },
    {
        key: 'yellow',
        container: outputBox7Container,
        image: outputImage7,
        loaderId: 'loader7',
        loaderText: 'Processing Yellow...',
        fnName: 'process_yellow_image'
    },
    {
        key: 'order',
        container: outputBox2Container,
        image: outputImage2,
        loaderId: 'loader2',
        loaderText: 'Processing Order...',
        fnName: 'process_order_image'
    },
    {
        key: 'orderO',
        container: outputBox3Container,
        image: outputImage3,
        loaderId: 'loader3',
        loaderText: 'Processing Order O...',
        fnName: 'order_o'
    },
    {
        key: 'orderC',
        container: outputBox4Container,
        image: outputImage4,
        loaderId: 'loader4',
        loaderText: 'Processing Order C...',
        fnName: 'order_c'
    },
    {
        key: 'orderOP',
        container: outputBox5Container,
        image: outputImage5,
        loaderId: 'loader5',
        loaderText: 'Processing Order OP...',
        fnName: 'order_op'
    },
    {
        key: 'orderOC',
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

function getActiveConfig() {
    return outputConfigs.find(config => config.key === outputSelect.value) || null;
}

async function processConfigs(configs, jobId) {
    if (!configs.length || !lastImageBytes) {
        return;
    }
    await pyodideLoadingPromise;
    if (!pyodide) {
        throw new Error("Pyodide not initialized.");
    }

    const imageBytesPy = pyodide.toPy(new Uint8Array(lastImageBytes));
    const tasks = configs.map(async (config) => {
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
        if (config.key === outputSelect.value) {
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

    const activeConfig = getActiveConfig();
    outputConfigs.forEach((config) => {
        if (activeConfig && config.key === activeConfig.key) {
            showLoader(config);
        } else {
            setOutputHidden(config);
        }
    });

    try {
        const reader = new FileReader();
        reader.onload = async (e) => {
            lastImageBytes = e.target.result;
            if (!activeConfig) {
                return;
            }
            try {
                await processConfigs([activeConfig], jobId);
            } catch (error) {
                console.error("Processing error:", error);
                setLoaderError(activeConfig);
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

outputSelect.addEventListener('change', async () => {
    const activeConfig = getActiveConfig();
    outputConfigs.forEach((config) => {
        if (!activeConfig || config.key !== activeConfig.key) {
            setOutputHidden(config);
        }
    });
    if (!activeConfig || !lastImageBytes) {
        return;
    }
    if (lastResults[activeConfig.key]) {
        showResult(activeConfig, lastResults[activeConfig.key]);
        return;
    }
    const jobId = currentJobId;
    showLoader(activeConfig);
    try {
        await processConfigs([activeConfig], jobId);
    } catch (error) {
        console.error("Processing error:", error);
        setLoaderError(activeConfig);
    }
});
