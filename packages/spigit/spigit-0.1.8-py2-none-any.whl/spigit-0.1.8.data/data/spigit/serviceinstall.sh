#! /bin/sh
#user input
echo "Example: /home/ubuntu/anaconda2/bin/python"
read -p "Enter anaconda path: " anacondapath
echo "Example: /home/ubuntu/repo/gitscript.py"
read -p "Enter full path to script: " scriptpath
#create temp file
cp service temp
#append paths
sed -i "16i\    ${anacondapath} ${scriptpath} &\\" temp
sed -i "20i\    killall ${anacondapath} ${scriptpath}\\" temp
#service vars
file=/etc/init.d/spigit
servicename=spigit
#check if service is already installed
if [ -e "$file" ]; then
    echo "$file exists already, replaced"
    rm $file
    cp temp $file
    rm temp
else
    echo "Service file copied to $file"
    cp temp $file
    rm temp
fi
#update service files
systemctl daemon-reload
chmod +x $file
update-rc.d $servicename defaults
