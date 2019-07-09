#!/usr/bin/env python
# coding: utf-8

# # Exercise 2
# 
# __What is this?__ This is a CMSSW configuration file
# 
# __Does it work on Jupyter?__
# Well... yes and no. Every CMSSW configuration file is a fully consistent python script, which means you can execute part of it in jupyter and see the effects, to run it on data, though you still need to export it in plain python and run it with `cmsRun`
# 
# __How do I export the notebook?__
# Simply run in a shell:
# 
# `jupyter nbconvert --to script Exercise2.ipynb`
# 
# 
# ## Part I - a crash course on CMSSW configs
# 
# Every CMSSW config must import the CMS standard configuration module and define a process. The process is the class that contains all the modules that _can_ be run, the __Path__s and __Sequence__s that _must_ be run.
# The process must have a name, and such name must be unique in the data chain, i.e. if the data have been processed by a process named `FOO`, you cannot run them again through a process with the same name
# It's necessary to specify the era considered, as different taggers may have different trainings for different eras, see https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCmsDriverEras

# In[ ]:


import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
process = cms.Process("USER",eras.Run2_2018)


# Calling `process.load(fragment_name)` will act very similarly to `import` in normal python, but all the CMSSW modules defined in the python fragment will be loaded directly into the process.
# For our purposes we need a bunch of services that define detector geometry and magnetic field map.

# In[ ]:


process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 10


# The `GlobalTag` defines a specific set of conditions (alignment, jet energy corrections etc.) valid for data or MC and for a specific set of range. You can look for the valid global tag for the data you are analyzing [here](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions?redirectedfrom=CMS.SWGuideFrontierConditions)

# In[ ]:


from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '102X_upgrade2018_realistic_v15')


# Of course, you can define the input files, the number of events to run on, and if you want a full summary of what has been run

# In[ ]:


#Source
process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring(
        'root://cmseos.fnal.gov//store/user/hats/2019/Tagging/TTToSemiLeptonic_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15/D7F68ED3-7D8A-0A4E-A53E-D5557F11760C.root'
    )
)

#Events to run
process.maxEvents = cms.untracked.PSet( 
    input = cms.untracked.int32(100) 
)

#Long summary
process.options = cms.untracked.PSet( 
    wantSummary = cms.untracked.bool(True) 
)


# This is how you define the output of the edm file

# In[ ]:


process.out = cms.OutputModule(
    "PoolOutputModule",
    fileName = cms.untracked.string('updated_btagging.root'),
    ## save only events passing the full path
    #SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
    outputCommands = cms.untracked.vstring(
        'drop *', ## Do not keep anything
        'keep *_slimmedJets_*_*' #keep only the slimmed jets
    )
)


# __The format of the `keep` statement:__ Stars are allowed and mean anything like in POSIX regular expressions (the one you use in your shell), there are four fields separated by an underscore, in the same order as presented by the `edmDumpEventContent` command. They represent:
#    1. The type of the object
#    2. The name (a.k.a _label_) of the module producing it
#    3. The _instance_. If a module produces multiple objects, it will make them with the same name, but different instances (and, potentially, types)
#    4. The process name. This is used in case you want to reproduce some objects in your cfg (e.g. the whole HLT simulation) and save only the new one

# In[ ]:


from PhysicsTools.PatAlgos.tools.helpers import getPatAlgosToolsTask
patAlgosToolsTask = getPatAlgosToolsTask(process)


# More information on what a `cms.Task` is are available [here](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideAboutPythonConfigFile#Task_Objects).
# 
# The EndPath contains the information of what needs to be run at the end of the execution of each event.

# In[ ]:


process.outpath = cms.EndPath(process.out, patAlgosToolsTask)


# ## Part II - remaking b-tag discriminators from MiniAOD
# 
# Everything is handled by a single helper function

# In[ ]:


from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection


# Getting the full set of optional arguments, unfortunately, is a bit cumbersome. This approach, though, _should_ be similar for all PAT-based modifier functions

# In[ ]:


print updateJetCollection.__doc__
for par_name, par in updateJetCollection._parameters.iteritems():
    print '   - %s:  %s' % (par_name, par.description)


# We now want to re-make deepCSV and CSVv2 from MiniAOD, please complete the next block with the necessary code.

# In[ ]:


updateJetCollection(
    process,
    jetSource = cms.InputTag('slimmedJets'),
    #we need to re-apply the JECs
    jetCorrections = ('AK4PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute']), 'None'), 
    btagPrefix = 'TEST',
    #
    # YOUR CODE HERE
    #
)


# Here you should write the necessary code to store the new discriminators. What will be their name?

# In[ ]:


#
# YOUR CODE HERE!
#


# Now you can convert the notebook to run on the data!
