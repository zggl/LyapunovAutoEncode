import torch
from AEPredNet import AEPredNet
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from matplotlib import colors

def tsne(model, X, tsne_params = {}):
	encoded = model(X)[1]
	tsne_model = TSNE(**tsne_params)
	X_embedded = tsne_model.fit_transform(encoded.detach().numpy())
	print(X_embedded.shape)
	return tsne_model
	
def main():
	if torch.cuda.is_available():
		device= torch.device('cuda')
	else: 
		device= torch.device('cpu')
	model = torch.load('ae_prednet_4000.ckpt')
	model.load_state_dict(model.best_state)
	x_data = torch.load('Processed/lstm_allLEs.p')
	split = torch.load('data_split_vfrac0.2.p')
	indices = [0, 300, 600, 900, 1200]
	sizes = [64, 128, 256, 512]
	tsne_model = tsne(model, split['train_data'], tsne_params = {'perplexity' : 10})
	splits = []
	i_list = torch.arange(1200)
	splits = [(i_list>torch.ones_like(i_list)*indices[i])*(i_list<torch.ones_like(i_list)*indices[i+1]) for i in range(len(indices)-1)]
	Y = tsne_model.fit_transform(x_data)
	for idx, size in enumerate(sizes):
		y = Y[splits[idx]]
		plt.scatter(y[:,0], y[:,1], s = 6)
	plt.legend()
	torch.save(Y, 'tsne.p')
	plt.savefig('AEPredNet_tsne_size.png', dpi = 200)

def param_plot():
	model = torch.load('ae_prednet_4000.ckpt')
	model.load_state_dict(model.best_state)
	x_data = torch.load('Processed/lstm_allLEs.p')
	params = torch.load('lstm_allParams.p')
	split = torch.load('data_split_vfrac0.2.p')
	indices = [0, 300, 600, 900, 1200]
	sizes = [64, 128, 256, 512]
	val_idx = split['val_idx']
	val_splits = []
	for i in range(len(sizes)):
		val_splits.append(((val_idx>torch.ones_like(val_idx)*indices[i])*(val_idx<torch.ones_like(val_idx)*indices[i+1])))
		# print(torch.arange(1200).float()>torch.ones(1200)*indices[i])
		# print(val_idx[val_splits[i]].shape)
		plt.scatter(params[val_idx[val_splits[i]]], model(x_data[val_idx[val_splits[i]]])[2].detach(), label = sizes[i], s = 14)
	plt.legend()
	plt.xlabel('Init Param')
	plt.ylim([1.1, 2.6])
	plt.ylabel('Validation Loss \n (Predicted)')
	plt.title('AE Predictions')
	plt.savefig('AEPredNet_paramPlot.png', bbox_inches="tight",dpi=200)
	
	plt.figure()
	targets = torch.load('Processed/lstm_allValLoss.p')
	for i in range(4): 
		plt.scatter(params[val_idx[val_splits[i]]], targets[val_idx[val_splits[i]]], label = sizes[i], s = 14)
	plt.legend(prop = {'size':12})
	plt.ylabel('Val Loss\n(Actual)')
	plt.xlabel('Init Param')
	plt.ylim([1.1, 2.6])
	plt.title(f'Ground Truth')
	plt.savefig('Actual_paramPlot.png', bbox_inches="tight",dpi=200)
	
def tsne_perf():
	indices = [0, 300, 600, 900, 1200]
	sizes = [64, 128, 256, 512]
	targets = torch.load('Processed/lstm_allValLoss.p')
	splits = []
	i_list = torch.arange(1200)
	splits = [(i_list>torch.ones_like(i_list)*indices[i])*(i_list<torch.ones_like(i_list)*indices[i+1]) for i in range(len(indices)-1)]
	Y = torch.load('tsne.p')
	for idx, size in enumerate(sizes):
		y = Y[splits[idx]]
		plt.scatter(y[:,0], y[:,1], s = 6, c = targets[splits[idx]], norm=colors.LogNorm(vmin=targets.min(), vmax=targets.max()))
	plt.colorbar(label = 'Val Loss')
	plt.xlabel('TSNE 1')
	plt.ylabel('TSNE 2')
	plt.savefig('AEPredNet_tsne_performance.png', dpi = 200)
	
def tsne_param():
	indices = [0, 300, 600, 900, 1200]
	sizes = [64, 128, 256, 512]
	params = torch.load('lstm_allParams.p')
	splits = []
	i_list = torch.arange(1200)
	splits = [(i_list>torch.ones_like(i_list)*indices[i])*(i_list<torch.ones_like(i_list)*indices[i+1]) for i in range(len(indices)-1)]
	Y = torch.load('tsne.p')
	for idx, size in enumerate(sizes):
		y = Y[splits[idx]]
		plt.scatter(y[:,0], y[:,1], s = 6, c = params[splits[idx]])#, norm=colors.LogNorm(vmin=params.min(), vmax=params.max()))
	plt.colorbar(label = 'Init Param')
	plt.xlabel('TSNE 1')
	plt.ylabel('TSNE 2')
	plt.savefig('AEPredNet_tsne_params.png', dpi = 200)
	
if __name__ == "__main__":
	tsne_param()