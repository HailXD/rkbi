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

        let pyodide = null;
        let pyodideLoadingPromise = null;

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
                outputBox1Container.insertAdjacentHTML('beforeend', '<p class="loader" id="loader1">Processing Portfolio...</p>');
                
                outputBox2Container.style.display = 'flex';
                outputImage2.style.display = 'none';
                outputBox2Container.insertAdjacentHTML('beforeend', '<p class="loader" id="loader2">Processing Order...</p>');

                outputBox3Container.style.display = 'flex';
                outputImage3.style.display = 'none';
                outputBox3Container.insertAdjacentHTML('beforeend', '<p class="loader" id="loader3">Processing Order O...</p>');

                outputBox4Container.style.display = 'flex';
                outputImage4.style.display = 'none';
                outputBox4Container.insertAdjacentHTML('beforeend', '<p class="loader" id="loader4">Processing Order C...</p>');

                outputBox5Container.style.display = 'flex';
                outputImage5.style.display = 'none';
                outputBox5Container.insertAdjacentHTML('beforeend', '<p class="loader" id="loader5">Processing Order OP...</p>');

                outputBox6Container.style.display = 'flex';
                outputImage6.style.display = 'none';
                outputBox6Container.insertAdjacentHTML('beforeend', '<p class="loader" id="loader6">Processing Order OC...</p>');

                try {
                    await pyodideLoadingPromise;
                    if (!pyodide) {
                        throw new Error("Pyodide not initialized.");
                    }

                    const reader = new FileReader();
                    reader.onload = async (e) => {
                        const imageBytes = e.target.result;

                        const imageBytesPy = pyodide.toPy(new Uint8Array(imageBytes));

                        let process_portfolio_image = pyodide.globals.get('process_portfolio_image');
                        let order_o = pyodide.globals.get('order_o');
                        let order_c = pyodide.globals.get('order_c');
                        let order_op = pyodide.globals.get('order_op');
                        let order_oc = pyodide.globals.get('order_oc');
                        let process_order_image = pyodide.globals.get('process_order_image');

                        const results = await Promise.all([
                            process_portfolio_image(imageBytesPy),
                            order_o(imageBytesPy),
                            order_c(imageBytesPy),
                            order_op(imageBytesPy),
                            order_oc(imageBytesPy),
                            process_order_image(imageBytesPy)
                        ]);

                        const parsedResults = results.map(r => JSON.parse(r));

                        console.log("Most common colors per image:", parsedResults.map(p => p.colors));

                        const loader1 = document.getElementById('loader1');
                        if(loader1) loader1.remove();
                        outputImage1.src = 'data:image/png;base64,' + parsedResults[0].image;
                        outputImage1.style.display = 'block';

                        const loader2 = document.getElementById('loader2');
                        if(loader2) loader2.remove();
                        outputImage2.src = 'data:image/png;base64,' + parsedResults[5].image;
                        outputImage2.style.display = 'block';

                        const loader3 = document.getElementById('loader3');
                        if(loader3) loader3.remove();
                        outputImage3.src = 'data:image/png;base64,' + parsedResults[1].image;
                        outputImage3.style.display = 'block';

                        const loader4 = document.getElementById('loader4');
                        if(loader4) loader4.remove();
                        outputImage4.src = 'data:image/png;base64,' + parsedResults[2].image;
                        outputImage4.style.display = 'block';

                        const loader5 = document.getElementById('loader5');
                        if(loader5) loader5.remove();
                        outputImage5.src = 'data:image/png;base64,' + parsedResults[3].image;
                        outputImage5.style.display = 'block';

                        const loader6 = document.getElementById('loader6');
                        if(loader6) loader6.remove();
                        outputImage6.src = 'data:image/png;base64,' + parsedResults[4].image;
                        outputImage6.style.display = 'block';
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
                    const loader3 = document.getElementById('loader3');
                    if(loader3) loader3.textContent = 'Error';
                    const loader4 = document.getElementById('loader4');
                    if(loader4) loader4.textContent = 'Error';
                    const loader5 = document.getElementById('loader5');
                    if(loader5) loader5.textContent = 'Error';
                    const loader6 = document.getElementById('loader6');
                    if(loader6) loader6.textContent = 'Error';
                }
            }
        });