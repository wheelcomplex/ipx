package main

import (
    "fmt"
    "net/http"
    "io/ioutil"
    "os"
)


func main() {
    client := &http.Client{}

    var url string = "http://ipx.sh"

    if len(os.Args) > 1 {
        switch {
          case os.Args[1] == "json":
            url = url + "/json"
          case os.Args[1] == "ping":
            if len(os.Args) > 2 {
              url = url + "/ping/" + os.Args[2]

              if  len(os.Args) > 3 {
                url = url + "/" + os.Args[3]
              }
            }
          case os.Args[1] == "rdr":
            // if len(os.Args) > 2 {
            //   target = os.Args[2]
            //   tcp.connect(server)
            //   tcp.connect(target)
            //   while(line = read.from(server)) {
            //      write.to(target)
            //      write.to(server, read.from(target))
            //   }
            // } else {
            //   os.Exit(1)
            // }

          case os.Args[1] == "xml":
            url = url + "/xml"
          case os.Args[1] == "ptr":
            url = url + "/ptr"
          case os.Args[1] == "a":
            if len(os.Args) > 2 {
              url = url + "/a/" + os.Args[2]

              if  len(os.Args) > 3 {
                url = url + "/" + os.Args[3]
              }
            }
        }
    }

    //fmt.Println(url)

    req, err := http.NewRequest("GET", url, nil)
    
    if err != nil {
        os.Exit(1)
    }

    req.Header.Add("User-Agent", "ipx")
    resp, err := client.Do(req)
    defer resp.Body.Close()

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        fmt.Println(err)
    }

    fmt.Println(string(body))
}


