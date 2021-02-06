<?php
echo "test";
$output = shell_exec('tail -n 150 /home/pi/testfrigo.csv');
echo "<pre>$output</pre>";
?>

