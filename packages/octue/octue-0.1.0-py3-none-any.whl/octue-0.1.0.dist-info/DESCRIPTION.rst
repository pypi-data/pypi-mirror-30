octue-sdk-python Application SDK for python-based apps on the Octue platform

MIT License

Copyright (c) 2017-2018 Octue Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Description: # octue-sdk-python <span><img src="http://slurmed.com/fanart/javier/213_purple-fruit-snake.gif" alt="Purple Fruit Snake" width="100"/></span>
        SDK for python based apps running within octue.
        
        
        ## Quickstart
        
        To create a python app for the octue platform:
         
         1. [fork this repository](https://guides.github.com/activities/forking/), or create a new repository and copy this repo's source code into it.
          
         2. Update the `name` field in `setup.py` to your application name (as registered on Octue), and apply a version number. Any version numbers are valid within Octue, but we strongly recommend either the [semantic versioning](http://semver.org) convention, or using the git hash of the currently checked out version (see `git rev-parse HEAD`)
         
         3. Connect your repo to the otue platform using our [github integration](). If you can't do that (e.g. if your repository is behind a firewall onsite), no problem - create a slug of the application code with:
         ```bash
            git clone --depth 1 git@server:repo.git $DEST
            rm -r $DEST/.git
            tar czvf repo.tgz $DEST
            rm -rf $DEST
         ```
         Then upload the slug to the application creation wizard on the octue platform.
         
         4. ...TODO
        
        
Platform: UNKNOWN
