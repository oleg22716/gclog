# gclog
gclog analyzer.

MLP2 - buisness logic, parser

main - flask logic

Works for parallelgc with following options:
CommandLine flags: -XX:+AggressiveOpts -XX:+AlwaysPreTouch -XX:+DisplayVMOutputToStderr -XX:-DisplayVMOutputToStdout -XX:InitialHeapSize=137438953472 -XX:LargePageSizeInBytes=2097152 -XX:MaxHeapSize=137438953472 -XX:+PrintGC -XX:+PrintGCApplicationStoppedTime -XX:+PrintGCDateStamps -XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:-ShowMessageBoxOnError -XX:+UseLargePages -XX:+UseNUMA -XX:+UseNUMAInterleaving -XX:+UseParallelGC 

working on processing different flags, along with different collectors.
should NOT work with damaged logs for now
also planning migration to Vue
