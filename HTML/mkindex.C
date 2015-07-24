#include <cstdlib>
#include <string>
#include <cstring>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <cmath>
#include <vector>
#include <stdio.h>
#include <algorithm>
using namespace std;

# ifndef __CINT__
int main(int argc, const char* argv[]) {
    if(argc < 4) {
        cout<<"Incorrect number of arguments"<<endl;
        exit(EXIT_FAILURE);
    }

    cout<<"Running!"<<endl;
    ofstream iWriter;
    cout<<"Opening file for writing: "<<argv[1]<<endl;
    iWriter.open(argv[1]);

    // get the list of files from argv[3]
    char tcar[256] = "ls -1 ";
    FILE* pipe = popen(strcat(tcar,argv[3]), "r");
    if(!pipe) {
        cout<<"ERROR: Unable to ls directory "<<argv[3]<<endl;
        exit(EXIT_FAILURE);
    }

    vector<string> filenames;
    char buffer[128];
    while(!feof(pipe)) {
        if(fgets(buffer,128,pipe) != NULL) {
            string buf = buffer;
            replace(buf.begin(), buf.end(), '\n', ' ');
            filenames.push_back(buf);
        }
    }

    // proceed to write the HTML
    iWriter << "<html><head>";
    // set the title using the second argument
    iWriter << "<title>" << argv[2] << "</title>";
    iWriter << "</head>";
    iWriter << "<body>";
    // set the style
    iWriter << "<style>";
    iWriter << "body { padding: 0; margin: 0; background-color: white; } ";
    iWriter << "div { position: relative; margin-left: auto; margin-right: auto; width: 600px; } ";
    iWriter << "div img,h3 { position: relative; margin-left: auto; margin-right: auto; width: 100%; } ";
    iWriter << "</style>";

    // add in the div to contain the images
    iWriter << "<div>";
    // iterate over the filename vector
    for(vector<string>::const_iterator i = filenames.begin(); i != filenames.end(); i++) {
        iWriter << "<h3>" << *i << "</h3>";
        iWriter << "<img src='" << *i << "'\\>";
        iWriter << "<br \\><br \\>";
    }

    iWriter << "</div>";
    iWriter << "</body>";
    iWriter << "</html>";

    iWriter.close();

    return 0;
}
# endif
