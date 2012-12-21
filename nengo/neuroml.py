import nef

import ca.nengo

import ca.nengo.util.MU as MU

net=nef.Network('NeuroMLTest', seed=1)
net.make('A',10,1)
net.make('B',5,1)
net.connect('A','B')
net.connect('B','B')
net.view()



class NeuroMLGenerator:
    header="""<neuroml xmlns="http://www.neuroml.org/schema/neuroml2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.neuroml.org/schema/neuroml2 http://neuroml.svn.sourceforge.net/viewvc/neuroml/NeuroML2/Schemas/NeuroML2/NeuroML_v2alpha.xsd"
  id="%s">
    <iafCell id="iaf" reset="-65mV" C="1.0 nF" thresh="-50mV" leakConductance="10 nS" leakReversal="-65mV"/>"""  #TODO: match values to our tau_rc value
        
    footer="""</neuroml>"""
    
    def __init__(self,net):
        self.net=net
        self.name=net.network.name
        self.bias_scale=0.01   #TODO: compute this correctly!
        self.weight_scale=1.0  # TODO: compute this correctly!
    
    def compute_weight_matrix(self, proj):
        orig=proj.origin
        term=proj.termination
        post=term.node
        transform=term.transform

        while hasattr(orig,'getWrappedOrigin'): orig=orig.getWrappedOrigin()
        
        decoder=orig.getDecoders()
        encoder=term.node.getEncoders()
            
        # scale by radius
        encoder=MU.prod(encoder,1.0/post.getRadii()[0])
        
        encoder=MU.prod(encoder, self.weight_scale)
        
        # scale by gain
        
        for i, n in enumerate(post.nodes):
            for j in range(len(encoder[i])):
                encoder[i][j]*=n.scale
        
        #encoder=MU.prodElementwise(encoder, [n.scale for n in post.nodes])

        w=MU.prod(encoder,MU.prod(transform,MU.transpose(decoder)))
        
        return w
            
        
    def generate(self):
        r=[]
        r.append(self.header%self.name)
        
        biases=[]
        inputs=[]
        populations=[]
        connections=[]
        synapses={}
        
        
        
        for node in self.net.network.nodes:
            if isinstance(node, ca.nengo.model.nef.impl.NEFEnsembleImpl):
                populations.append('      <population id="%s" component="iaf" size="%d"/>'%(node.name, node.neurons))
                nodes=node.nodes
                for i, n in enumerate(nodes):
                    id=len(biases)
                    bias=n.bias                
                    biases.append('    <pulseGenerator id="pulseGen_%d" delay="0ms" duration="100ms" amplitude="%f nA"/>'%(id, bias*self.bias_scale))
                    inputs.append('      <explicitInput input="pulseGen_%d" target="%s[%d]"/>'%(id, node.name, i))
        for p in self.net.network.projections:
            if isinstance(p.origin.node, ca.nengo.model.nef.impl.NEFEnsembleImpl) and isinstance(p.termination.node, ca.nengo.model.nef.impl.NEFEnsembleImpl):
                w=self.compute_weight_matrix(p)
                tau=p.termination.tau
                tau_ms=int(tau*1000+0.5)
                if tau_ms not in synapses:
                    synapses[tau_ms]='    <expOneSynapse id="syn%d" erev="0mV" gbase="65nS" tauDecay="%dms"/>'%(tau_ms, tau_ms)
                synid='syn%d'%(tau_ms)

                
                for i in range(p.origin.node.neurons):
                    for j in range(p.termination.node.neurons):
                        # TODO: include connection weight w[i][j] in here somewhere
                        connections.append('      <synapticConnection from="%s[%d]" to="%s[%d]" synapse="%s"/>'%(p.origin.node.name, i, p.termination.node.name, j, synid))
                        
       
        
        r.extend(synapses.values())
        r.extend(biases)
        r.append('    <network id="%s">'%self.name)
        r.extend(populations)
        r.extend(connections)
        r.extend(inputs)
        r.append('    </network>')
        
        
        r.append(self.footer)        
        return '\n'.join(r)    


g=NeuroMLGenerator(net)

open('%s.xml'%net.network.name,'w').write(g.generate())
