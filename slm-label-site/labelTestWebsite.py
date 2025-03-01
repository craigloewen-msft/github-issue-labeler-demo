from flask import Flask, render_template, request

import sys
import json

import torch
from utils import (load_tokenizer, load_model, load_peft_model, get_device, 
                   generate_text, run_prompt, check_adapter_path, generate_string)

import os

app = Flask(__name__)

class LabelManager:
    def __init__(self):
        self.initialized = False
        self.labels = []
        self.model_name = "../model-cache/microsoft/Phi-3-mini-4k-instruct"
        self.adapters_name = "../models/qlora/qlora/gpu_model/adapter"  # Ensure this path is correctly set before running
        self.torch_dtype = torch.bfloat16  # Set the appropriate torch data type
        self.quant_type = 'nf4'  # Set the appropriate quantization type
        self.model = None

    def initialize(self):
        check_adapter_path(self.adapters_name)
        self.tokenizer = load_tokenizer(self.model_name)

        self.model = load_model(self.model_name, self.torch_dtype, self.quant_type)
        self.model.resize_token_embeddings(len(self.tokenizer))

        usingAdapter = False
        if os.path.exists(self.adapters_name):
            self.model = load_peft_model(self.model, self.adapters_name)


        self.device = get_device()
        self.initialized = True

    def hasInitialized(self):
        return self.initialized

    def getLabels(self, inputString):
        template = "<|user|>\nPlease output the labels for this GitHub issue as a comma separated list:\n\n===Issue Info===\n\n{}\n\n===Labels to apply===\n<|end|>\n<|assistant|>"
        resultString = generate_string(self.model, self.tokenizer, self.device, inputString, template)
        return resultString
    
labelManager = LabelManager()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/calculateLabels', methods=['POST'])
def get_ticket_labels():
    data = request.get_json()
    
    if not labelManager.hasInitialized():
        return "Error: Not initialized"

    if 'inputText' not in data:
        return "Error: No inputText provided"
    
    returnLabels = labelManager.getLabels(data['inputText'])
    
    return returnLabels

@app.route('/api/loadModel')
def loadModel():
    
    labelManager.initialize()
    
    return "Model loaded!"

if __name__ == '__main__':
    app.run(debug=True)