#!/bin/bash
#                 ██████╗███████╗██╗   ██╗    ███████╗██████╗ ██╗     ██╗████████╗████████╗███████╗██████╗ 
#                ██╔════╝██╔════╝██║   ██║    ██╔════╝██╔══██╗██║     ██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗
#                ██║     ███████╗██║   ██║    ███████╗██████╔╝██║     ██║   ██║      ██║   █████╗  ██████╔╝
#                ██║     ╚════██║╚██╗ ██╔╝    ╚════██║██╔═══╝ ██║     ██║   ██║      ██║   ██╔══╝  ██╔══██╗
#                ╚██████╗███████║ ╚████╔╝     ███████║██║     ███████╗██║   ██║      ██║   ███████╗██║  ██║
#                 ╚═════╝╚══════╝  ╚═══╝      ╚══════╝╚═╝     ╚══════╝╚═╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝

# Example:  sh CSV_splitter.sh --input /Volumes/ALEJANDRO/S.E./Credit-Card-Fraud-Detection/Datasets/master.csv 
# --train_ratio 80 --save_train /Volumes/ALEJANDRO/S.E./Credit-Card-Fraud-Detection/Datasets --save_test /Volumes/ALEJANDRO/S.E./Credit-Card-Fraud-Detection/Datasets --shuffle

# Starts with 0.
SHUFFLE=0

while [[ $# -gt 0 ]]; do
    key=$1 
    case $key in 
        --input)
            INPUT=$2
            shift 2
            ;;
        --shuffle)
			SHUFFLE=1
            shift 1
            ;;
        --train_ratio)
            TRAIN_RATIO=$2
            shift 2
            ;;
        --save_train)
            SAVE_TRAIN=$2
            shift 2
            ;;
        --save_test)
            SAVE_TEST=$2
            shift 2
            ;;
        *)
            INPUT=$1
            shift 1
            ;;
    esac
done

if [[ ! "$INPUT" ]]; then
    echo "The path to the dataset must be provided"
    exit 1
fi
if [[ ! "$TRAIN_RATIO" ]]; then
    echo "The train ratio must be provided"
    exit 1
fi
if [[ ! "$SAVE_TRAIN" ]]; then
    echo "The test output must be provided"
    exit 1
fi
if [[ ! "$SAVE_TEST" ]]; then
    echo "The path for test output must be provided"
    exit 1
fi

shuffle()
{
	awk 'BEGIN{srand() }
	{ lines[++d]=$0 }
	END{
		while (1){
		if (e==d) {break}
			RANDOM = int(1 + rand() * d)
			if ( RANDOM in lines  ){
				print lines[RANDOM]
				delete lines[RANDOM]
				++e
			}
		}
	}' $1 > shuffle.data
}

echo
echo 'Input '$INPUT
echo 'Suffle '$SHUFFLE
echo 'Train ratio '$TRAIN_RATIO
echo 'Train '$SAVE_TRAIN
echo 'Values '$SAVE_TEST
echo

# The header is extracted.
header=$(head -1 $INPUT);
# The data is separeted from the header.
tail -n +2 $INPUT > output.data;
# If specified the data is shuffled.
if [ $SHUFFLE == "yes" ] || [ $SHUFFLE == "1" ];
then
	# Path to the auxiliar CSV.
	aux_path=$(pwd)/output.data
	shuffle $aux_path;
	# Unshuffled data is deleted.
	rm -f output.data
	# The number of lines of the aux CSV is captured.
	shuffle_path=$(pwd)/shuffle.data
	number_of_lines=$(wc -l $shuffle_path | tr -dc '0-9');
	# The number of necesary lines is extracted, for his later use on the training.
	train=$(($TRAIN_RATIO*$number_of_lines/100));
	# Train file was generated.
	head -n $train shuffle.data >$SAVE_TRAIN/training.csv;
	# The header of the training it's added to the CSV.
	tmp=/var/tmp/$$.tmp;
	echo $header > $tmp;
	cat $SAVE_TRAIN/training.csv >> $tmp;
	cat $tmp > $SAVE_TRAIN/training.csv;
	# test was generated.
	tail -n $(($number_of_lines-$train)) shuffle.data >$SAVE_TEST/test.csv;
	# The header of the test it's added to the CSV.
	echo $header > $tmp;
	cat $SAVE_TEST/test.csv >> $tmp;
	cat $tmp > $SAVE_TEST/test.csv;
	rm -f  $tmp 2>/dev/null && rm -f shuffle.data;
elif [ $SHUFFLE == "no" ] || [ $SHUFFLE == "0" ];
then
	# The number of lines of the aux CSV is captured.
	aux_path=$(pwd)/output.data
	number_of_lines=$(wc -l $aux_path | tr -dc '0-9');
	# The number of necesary lines is extracted, for his later use on the training.
	train=$(($TRAIN_RATIO*$number_of_lines/100));
	# Train file was generated.
	head -n $train output.data >$SAVE_TRAIN/training.csv;
	# The header of the training it's added to the CSV.
	tmp=/var/tmp/$$.tmp;
	echo $header > $tmp;
	cat $SAVE_TRAIN/training.csv >> $tmp;
	cat $tmp > $SAVE_TRAIN/training.csv;
	# test was generated.
	tail -n $(($number_of_lines-$train)) output.data >$SAVE_TEST/test.csv;
	# The header of the test it's added to the CSV.
	echo $header > $tmp;
	cat $SAVE_TEST/test.csv >> $tmp;
	cat $tmp > $SAVE_TEST/test.csv;
	rm -f  $tmp 2>/dev/null && rm -f output.data;
else
	echo 
	read -p "Introduce 1 and 0 or yes or no as second argument, press any key to exit";
	exit 1;
fi