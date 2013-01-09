# This assumes you have the latest verisons of jLEMS and NeuroML2 checked out locally, see:

# https://github.com/robertcannon/jLEMS
# https://github.com/NeuroML/NeuroML2
#
# Remember to build jLEMS with: ant
#
# Usage: ./runlems.sh LEMS_SimpleSpikingNet.xml

JLEMS_HOME=$HOME/jLEMS
NML2_HOME=$HOME/NeuroML2

export CLASSPATH=$JLEMS_HOME/builtjars/lems.jar

java -Xmx400M -classpath $CLASSPATH org.lemsml.jlemsviz.VizMain -cp $NML2_HOME/NeuroML2CoreTypes $1 $2 $3 $4

