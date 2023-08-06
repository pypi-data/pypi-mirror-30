from setuptools import setup

setup(
	name = 'py3hlda',
	packages = ['py3hlda'],
	version = '0.1.1',
	description = 'Gibbs sampler for the Hierarchical Latent Dirichlet Allocation topic model. This is based on the hLDA implementation from Mallet, having a fixed depth on the nCRP tree.',
	author = 'co',
	url = 'https://github.com/Jiannan28/hlda', 
	keywords = ['topic', 'model', 'lda', 'gibbs', 'sampler', 'hlda'], 
	classifiers = [],
	zip_safe=False
)