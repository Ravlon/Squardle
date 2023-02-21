from string import ascii_lowercase
from tqdm import tqdm
import pathlib
from Luca.utils import yes
from Squardle.src.board_parser import *
from time import time
from Luca.logger import LucaLogger
logger = LucaLogger(__name__)

MIN_LENGHT = 4
PROPER_NOUN = []
PATH = pathlib.Path(__file__).parent.parent.absolute()

def neighbours(row:int, col:int, shape:tuple, matrix:list):
    """Generate all possible neighbours of a grid's position.

    Args:
        row (int): row of the position of which neighbours are being calculated
        col (int): column of the position of which neighbours are being calculated
        shape (tuple): shape of the grid
        matrix (list): content of the grid

    Returns:
        list of tuple: list of tuple of neighbours's position [(row,column)]
    """
    #check and raise error for outofbound position
    try:
        return [(row+i,col+j) for i in range(-1,2) for j in range(-1,2) if abs(i)+abs(j) and row+i<shape[0] and col+j<shape[1] and row+i>-1 and col+j>-1 and matrix[row+i][col+j] in ascii_lowercase]
    except:
        logger.error("Unable to calculate Neighbours")
        return [0]

def make_matrix(board:list):
    """Generate a matrix given the board retrieved. Attach also all possible neighbors of the cells.
    Empy cells will not have or be neighbours. This allows waffle's boards.
    
    Args:
        board (list): squardle board as list of strings (the rows)

    Returns:
        Matrix of list: matrix with a list of the content of the cell and the possible neighbours 
    """
    board_matrix =  [list(row) for row in board]
    shape = (len(board_matrix[0]),len(board_matrix))
    result = [[(" ",[]) for c in range(shape[1])] for r in range(shape[0])]
    try:
        for r in range(shape[0]):
            for c in range(shape[1]):
                if board_matrix[r][c] in ascii_lowercase:
                    result[r][c] = (board_matrix[r][c], neighbours(r,c,shape,board_matrix))
        logger.info("Successful creation of matrix of board with neighbours")
    except:
        logger.error("No Matrix available for prosecution of program")
    return result

def dictionary_maker(list1 = True, json_l = True, mill_list = True, given_word_list=[]):
    """List of all words that will be checked against by the solver.
    Retrieve words from saved files and make a set of all the available words.

    Args:
        list1 (bool, optional): Smallest list of possible 4-15-long words. Parse from Wordfinderx. Defaults to True.
        json_l (bool, optional): Other list of possible 4+ words. Given by Matteo . Defaults to True.
        mill_list (bool, optional): 1.5 million words of lengh 1+. Given by Matteo. Defaults to True.

    Returns:
        List: List of unique words of lengh 4 or more
    """
    WORD_PATH = PATH.joinpath("assets").joinpath("words")
    wordfinder_link = WORD_PATH.joinpath("words_list.txt")
    json_link = WORD_PATH.joinpath("json_list.txt")
    million_link = WORD_PATH.joinpath("wlist_match1.txt")
    word_list = []
    if list1:
        try:
            with open(wordfinder_link, "r") as f:
                word_list.extend(tqdm([line.rstrip() for line in f.readlines()]))
            logger.debug("Wordfinderx List Uploaded")
        except:
            logger.warning("Wordfinderx List not available")
    if json_l:
        try:
            with open(json_link, "r") as f:
                word_list.extend(tqdm([line.rstrip() for line in f.readlines()]))
            logger.debug("Json List Uploaded")
        except:
            logger.warning("Json List not available")
    if mill_list:
        try:
            with open(million_link,"r") as f:
                word_list.extend(tqdm([line.rstrip() for line in f.readlines() if line.rstrip().isalpha() and len(line)>4]))
            logger.debug("Million and a Half List Uploaded")
        except:
            logger.warning("Million and a Half List not available")
    word_list.extend(given_word_list)
    word_list = set(word_list)
    word_list = sorted([w for w in word_list])
    message = "Word List is of size {0} words".format(len(word_list))
    logger.info(message)
    return word_list

def recursive_words(curr_word, trail, matrix, found_words:set, dictionary):
    """Recursive Function that allows to check for all possible words.
    Given a certain cell, it looks at all possible neighbours. Avoid the ones that are currently in use.
    It checks if the current word(4+) allows for any possible word in 'dictionary'.
    If a match is found the word is added to the results.
    If the dictionary show further possible words, the function calls itself back connecting itself to the neighbours.

    If no neighbours are found left then the function returns 0 and 'steps back' in the recursive calls.
    If no possible words are left in the dictionary matching the current word the function returns 0 and 'steps back' in the recursive calls.

    Args:
        curr_word (_type_): Current word being created and check by the recursive calls.
        trail (_type_): List of all visited cells that are forming the curren word being checked. This avoid double counting the same cell as this is not allowed.
        matrix (_type_): Grid in which the recursive function if operating. Each cell is a list of the letter contained and all possible neighbours to which the recursive function may connect.
        found_words (set): set of all matching words that have been found. No duplicates.
        dictionary (_type_): Current selection of the dictionary. The list is filtered to only have word beginning with the current word being checked.

    Returns:
        set: set of all possible words found in the board.
    """
    r = trail[-1][0]
    c = trail[-1][1]

    size = len(curr_word)
    
    try:
        if len(dictionary):                     #check enough words left
            if size >= MIN_LENGHT:    #check for words if len is >3
                filtered_dictionary = [word for word in dictionary if word[:size] == curr_word]
                for word in filtered_dictionary:
                    if len(word) == size:
                        found_words.add(word)
            else:
                filtered_dictionary = dictionary
        else:
            return found_words
    except:
        message = "Error encountered while filtering word list at trail: {0}".format(trail)
        logger.error(message)
        return found_words
    
    for i in matrix[r][c][1]:
        try:    
            if i not in trail:
                trailer = trail + [i]
                foll_word = curr_word + matrix[i[0]][i[1]][0]
                found_words = recursive_words(foll_word, trailer, matrix, found_words, filtered_dictionary)
            else:
                continue
        except:
            message = "Error encountered at trail: {0} while attempting to continue to {1}".format(trail,i)
            logger.error(message)
    return found_words

def board_solver(board:list, dictionary:list,verbose=False):
    """Initiate the recursive function to find all possible words in the board.

    Args:
        board (list): board of the day
        dictionary (list): list of all the words.
        verbose (bool, optional): Receive info about the result of the search. Number of words found and Optional list of the words found. Defaults to False.

    Returns:
        List: All the words found in the board. No duplicates.
    """
    #initiate recurive function to search for all possible words
    matrix = make_matrix(board)
    words = set()
    for r in tqdm(range(len(matrix))):
        for c in tqdm(range(len(matrix[0]))):
            try:
                words = recursive_words(matrix[r][c][0],[(r,c)], matrix, words, dictionary)
            except:
                message = "Error encountered in position ({0},{1}), letter {2} with initiated recursive solver".format(r,c,matrix[r][c][0])
    
    message = "Solver found {0} words suitable for the board".format(len(words))
    logger.info(message)

    #verbose mode shows number of words found and words found
    if verbose:
        print("Found words are: " + str(len(words)))
        if yes("Show found words? "):
            for i in words:
             print(i)
    
    return words

def invalid_words():
    """Retrieves list of proper nouns that squardle does not accept.

    TODO: check that nouns list hasn't changed.
    https://squaredle.app/api/static/names-short.csv

    Returns:
        List: of proper nouns
    """
    nouns_link = PATH.joinpath("assets").joinpath("proper_noun.txt")
    try:
        with open(nouns_link,"r") as f:
            return [word.rstrip() for word in f.readlines()]
    except:
        logger.error("Proper Nouns List not available")

def squardle_solver(quick_solution = True, quick_list = []):
    """ Retrieves all the necessary info of the day's board.
        Creates list of all words.
        Recursively find all possible words of the board
        Return all info necessary for Bot to execute.

        TODO: make a ranking of all words to increase accuracy and speed.

    Returns:
        words found: list of words that could possibly work in the squardle board
        bonus words: bonus word of the day. In case you want to put it at the end and avoid the pop up
        invalid words: list of invalid words that squardle doesn't accept. Skip these if present in solution list. Also to avoid pop ups.
    """
    try:
        setup = js_parser()
        board, bonus_word = day_setup(setup)
    except:
        logger.critical("Unable to get board of the day")
        return 0,0,0

    if quick_solution:
        word_list = dictionary_maker(mill_list=False)
        logger.info("Generation of Word List Optimized for Speed Completed")
    else:
        word_list = dictionary_maker(list1=False, json_l=False, mill_list=True, given_word_list=quick_list)
        logger.info("Generation of Word List optimized for Bonus Word Search Completed")
    try:
        start = time()
        solution = board_solver(board,word_list)
        stop = time()
        if quick_solution:
            message = "Board Solved Optimized for Speed - time:{0}s".format(round(stop-start,2))
        else:
            message = "Board Solved Optimized for Bonus Word - time:{0}s".format(round(stop-start,2))
        logger.info(message)
    except:
        logger.critical("Unable to solve BoardSolver")
        return 0,0,0
    return list(solution),bonus_word,invalid_words()


# var gContractions = "'twas 'tween 'twere ain't aren't can't could've couldn't couldn't've daren't daresn't didn't doesn't don't everybody's everyone's had've hadn't hasn't haven't here's how'd how'll how're how's i'd've isn't it'll ma'am may've might've mightn't must've mustn't mustn't've needn't ne'er o'clock ought've oughtn't oughtn't've shan't she's should've shouldn't somebody's someone's something's that'd that'll there'd there'll there's they'd they'll they're they've wasn't we'd've we've weren't what'd what'll what're what's what've when'd when's where'd where'll where's where've which's which've who'd who'd've who'll who're who's who've why'd why're why's won't would've wouldn't wouldn't've y'all you'd you'll you're you've".split(" ");
# var gBannedGuesses = "abos;amakwerekwere;arse;arses;arsing;asshole;baas;baases;backra;backras;bakra;bakras;ballbag;ballbags;ballsack;bastard;bastards;batshit;beaner;beaners;beastiality;bender;biatch;biatches;binghi;binghis;bint;bints;bitch;bitched;bitches;bitchiness;bitching;bitchy;blackamoor;blackamoors;blackfella;blackfellas;blowjob;boche;boches;bogtrotter;bogtrotters;bohunk;bohunks;bollock;bollocks;boner;boong;boonga;boongas;boongs;bosche;bosches;bossboy;bossboys;brushite;bubba;bubbas;buckra;buckras;buftie;bufties;bufty;bukkake;bulldike;bulldikes;bulldyke;bulldykes;bullshit;bullshits;bullshitted;bullshitter;bullshitters;bullshitting;bumboy;bumboys;buttmunch;buttplug;chickenshit;chickenshits;chinkie;chinkies;cholo;cholos;clit;cocksucker;cocksuckers;coolie;coolies;cooly;coon;coonshit;coonshits;copperskin;copperskins;cracka;crackas;crap;crapped;crapper;crapping;crip;crippledom;crippledoms;crips;cummed;cummer;cumming;cums;cumshot;cunt;cunts;cunty;dago;dagoes;dagos;darkey;darkeys;darkie;darkies;darky;dick;dicked;dicking;dicks;dikey;dikier;dikiest;dildo;dipshit;dipshits;dogan;dogans;douche;douchebag;douchebags;dyke;dykey;dykier;dykiest;faggeries;faggery;faggier;faggiest;fagging;faggot;faggotier;faggotiest;faggotries;faggotry;faggots;faggoty;faggy;fags;fatass;fatasses;fellate;fellatio;frig;frigged;frigging;frigs;fuck;fucked;fucker;fuckers;fuckface;fuckfaces;fuckhead;fuckheads;fucking;fuckoff;fuckoffs;fucks;fuckup;fuckups;fuckwit;fuckwits;fudgepacker;gammat;gammats;gangbang;gaylord;gaysex;ginzo;ginzoes;ginzos;gipped;gipping;gippo;gippoes;gippos;gips;gobshite;gobshites;golliwog;golliwogg;golliwoggs;golliwogs;gollywog;gollywogs;gook;gookeye;gookeyes;gooks;gooky;gookys;goyim;goyisch;goyish;goyishe;goys;gringa;gringas;gringo;gringos;guinea;gypo;gypos;gypped;gypper;gyppers;gypping;gyppo;gyppos;gyps;gypsied;gypsies;gypster;gypsters;gypsy;gypsying;haole;haoles;harelip;harelipped;harelips;hasbian;hasbians;hebe;hebes;hentai;honkey;honkeys;honkie;honkies;honky;hori;horis;horniest;horny;horseshit;horseshits;humping;hunkey;hunkeys;hunkie;hunkies;incest;incests;incestuous;incestuously;incestuousness;incestuousnesses;injun;injuns;jackoff;jerkoff ;jerries;jerry;jerrys;jesuit;jesuitic;jesuitical;jesuitically;jesuitism;jesuitisms;jesuitries;jesuitry;jesuits;jewboy;jewboys;jigaboo;jigaboos;jism;jizm ;jizz;kaffir;kaffirboom;kaffirbooms;kaffirs;kafir;kafirs;kanaka;kanakas;kike;kikes;knobhead;knobjocky;kraut;krauts;langer;langers;lesbo;lesbos;leses;lezes;lezz;lezza;lezzas;lezzes;lezzie;lezzies;lezzy;lubra;lubras;massa;massas;merde;mick;micks;mierda;mindfuck;mindfucked;mindfucks;minge;minges;moffie;moffies;mofo;mong;monged;mongol;mongolian;mongolism;mongolisms;mongoloid;mongoloids;mongols;mongs;motherfucker;motherfuckers;motherfucking;mulatress;mulatresses;mulatta;mulattas;mulatto;mulattoes;mulattos;mulattress;mulattresses;munt;munts;muntu;muntus;nance;nances;nancier;nancies;nanciest;nancified;nancy;neger;negress;negresses;negro;negroes;negrohead;negroheads;negroid;negroidal;negroids;negroism;negroisms;negrophil;negrophile;negrophiles;negrophilism;negrophilisms;negrophilist;negrophilists;negrophils;negrophobe;negrophobes;negrophobia;negrophobias;negros;nelly;nigga;niggah;nigger;niggerdom;niggerdoms;niggered;niggerhead;niggerheads;niggerier;niggeriest;niggering;niggerish;niggerism;niggerisms;niggerling;niggerlings;niggers;niggery;niglet;niglets;nitchie;nitchies;nonhandicapped;nonpapist;nonpapists;numbnuts;nutsack;nutsacks;octaroon;octaroons;octoroon;octoroons;ofay;ofays;papish;papisher;papishers;papishes;papism;papisms;papist;papistic;papistical;papistically;papistries;papistry;papists;peckerwood;peckerwoods;phonesex;picaninnies;picaninny;piccanin;piccaninnies;piccaninny;piccanins;pickaninnies;pickaninny;pickney;pickneys;pikey;pikeys;piss;polack;polacks;poofier;poofiest;poofs;pooftah;pooftahs;poofter;poofters;poofy;poove;pooveries;poovery;pooves;poovier;pooviest;poovy;poperies;popery;popish;popishly;porn;porno;pornographic;pornography;pornos;porns;pouftah;pouftahs;poufter;poufters;pube;pubes;pussies;pussy;quadroon;quadroons;quarteroon;quarteroons;quashee;quashees;quashie;quashies;queerdom;queerdoms;quintroon;quintroons;raghead;ragheads;rape;raped;rapes;raping;redneck;rednecked;rednecks;redskin;redskins;reffo;reffos;retard;retardate;retardates;retarded;retards;sakai;sakais;sambo;sambos;schizier;schiziest;schizo;schizos;schizy;schizzier;schizziest;schizzy;schvartze;schvartzes;schwartze;schwartzes;semimute;semimutes;shat;sheeney;sheeneys;sheenie;sheenies;shegetz;shemale;shemales;shicksa;shicksas;shiksa;shiksas;shikse;shikseh;shiksehs;shikses;shirtlifter;shirtlifters;shit;shitbag;shitbags;shitcan;shitcans;shite;shites;shitface;shitfaced;shitfaces;shithead;shitholes;shithteads;shitlist;shits;shitshole;shitstorm;shitstorms;shitte;shitted;shittier;shittiest;shittiness;shitting;shitty;shkotzim;shvartze;shvartzes;shylock;shylocks;skank;skanks;skanky;skimo;skimos;spastics;spaz;spazz;spazzed;spazzes;spazzing;spic;spick;spicks;spics;spik;spiks;squaw;squawman;squawmen;squaws;taig;taigs;thot;thots;tits;tittiefucker;titties;titty;towelhead;towelheads;trannie;trannies;tranny;twat;twinkie;twinkies;umlungu;umlungus;vendu;vendus;wang;wank;wanked;wanker;wankier;wankiest;wanking;wanks;wanky;welch;welched;welches;welching;welsh;welshed;welshes;welshing;wench;wetback;wetbacks;whitey;whiteys;whities;whore;wigga;wiggas;wigger;wiggers;willy;woggish;wogs;wooftah;wooftahs;woofter;woofters;yids;zambo;zambos".split(";"),
#     gInappropriateWords = "asshole;ballsack;batshit;blowjob;boner;brushite;bukkake;bullshit;bullshits;bullshitted;bullshitter;bullshitters;bullshitting;buttmunch;buttplug;chickenshit;chickenshits;clit;coonshit;coonshits;cummer;cunt;cunts;cunty;dildo;dipshit;dipshits;fagging;faggot;fags;fellate;fellatio;frig;frigged;frigging;frigs;fuck;fucked;fucker;fuckers;fuckface;fuckfaces;fuckhead;fuckheads;fucking;fuckoff;fuckoffs;fucks;fuckup;fuckups;fuckwit;fuckwits;fudgepacker;gangbang;gaylord;gaysex;gobshite;gobshites;harelip;hentai;horniest;horny;horseshit;horseshits;jackoff;jerkoff ;jism;jizm ;jizz;knobhead;knobjocky;merde;mierda;mindfuck;mindfucked;mindfucks;mofo;motherfucker;motherfuckers;motherfucking;nigga;nigger;piss;porn;porno;pornographic;pornography;pornos;porns;pussies;pussy;shat;shit;shitbag;shitbags;shitcan;shitcans;shite;shites;shitface;shitfaced;shitfaces;shithead;shitholes;shithteads;shitlist;shits;shitshole;shitstorm;shitstorms;shitte;shitted;shittier;shittiest;shittiness;shitting;shitty;tittiefucker;titties;wang;wank;wanker;wankier;wankiest;wanky;wench;whore;willy".split(";");