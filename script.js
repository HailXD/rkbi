        const uploadBox = document.getElementById('uploadBox');
        const fileInput = document.getElementById('fileInput');
        const previewImage = document.getElementById('previewImage');
        const uploadText = document.getElementById('uploadText');
        
        const outputBox1Container = document.getElementById('outputBox1Container');
        const outputImage1 = document.getElementById('outputImage1');
        const outputBox2Container = document.getElementById('outputBox2Container');
        const outputImage2 = document.getElementById('outputImage2');

        let pyodide = null;
        let pyodideLoadingPromise = null;

        async function initPyodide() {
            if (!pyodide) {
                uploadText.textContent = 'Loading Python Environment...';
                pyodide = await loadPyodide();
                await pyodide.loadPackage(["numpy", "Pillow", "requests"]);
                
                const orderCode = await (await fetch('order.py')).text();
                pyodide.runPython(orderCode);
                
                const portfolioCode = await (await fetch('portfolio.py')).text();
                pyodide.runPython(portfolioCode);

                uploadText.textContent = 'Python Ready. Upload Image.';
            }
            return pyodide;
        }
        
        pyodideLoadingPromise = initPyodide().catch(err => {
            console.error("Pyodide initialization failed:", err);
            uploadText.textContent = 'Error loading Python. Try refreshing.';
        });


        uploadBox.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (file) {
                uploadText.style.display = 'none';
                previewImage.src = URL.createObjectURL(file);
                previewImage.style.display = 'block';

                outputBox1Container.style.display = 'flex';
                outputImage1.style.display = 'none';
                outputBox1Container.insertAdjacentHTML('beforeend', '<p class="loader" id="loader1">Processing Image 1...</p>');
                
                outputBox2Container.style.display = 'flex';
                outputImage2.style.display = 'none';
                outputBox2Container.insertAdjacentHTML('beforeend', '<p class="loader" id="loader2">Processing Image 2...</p>');

                try {
                    await pyodideLoadingPromise;
                    if (!pyodide) {
                        throw new Error("Pyodide not initialized.");
                    }

                    const reader = new FileReader();
                    reader.onload = async (e) => {
                        const imageBytes = e.target.result;

                        const imageBytesPy = pyodide.toPy(new Uint8Array(imageBytes));

                        let result1Base64 = await pyodide.globals.get('process_portfolio_image')(imageBytesPy);
                        let result2Base64 = await pyodide.globals.get('process_order_image')(imageBytesPy);
                        
                        const loader1 = document.getElementById('loader1');
                        if(loader1) loader1.remove();
                        outputImage1.src = 'data:image/png;base64,' + result1Base64;
                        outputImage1.style.display = 'block';

                        const loader2 = document.getElementById('loader2');
                        if(loader2) loader2.remove();
                        outputImage2.src = 'data:image/png;base64,' + result2Base64;
                        outputImage2.style.display = 'block';

                    };
                    reader.readAsArrayBuffer(file);
                } catch (error) {
                    console.error("Processing error:", error);
                    uploadText.textContent = 'Error processing image.';
                    uploadText.style.display = 'block';
                    previewImage.style.display = 'none';
                    
                    const loader1 = document.getElementById('loader1');
                    if(loader1) loader1.textContent = 'Error';
                    const loader2 = document.getElementById('loader2');
                    if(loader2) loader2.textContent = 'Error';
                }
            }
        });