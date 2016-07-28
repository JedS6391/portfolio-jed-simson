Title:   Bencode Parsing in Swift
Summary: Thoughts about using Swift to create a Bencode parser.
Author:  Jed Simson
Date:    July 27, 2016
Tags:    Bencode, Swift, Parsing, Personal, Code

Recently I decided to look further into the BitTorrent Protocol, as I have been fascinated by distributed systems (like peer-to-peer) and the communication protocols involved.

As I learnt more about how the protocol works, I thought it would be a good exercise to create a parser for the [Bencode](https://en.wikipedia.org/wiki/Bencode) format, used to store and transfer metadata about a torrent file. My main goal was to create a simple program that simply constructs an internal representation of the Bencoded string and can output in a nicer format (such as JSON).

---

## Bencode

Bencode is a fairly simple encoding which has four different types:

**Byte Strings**

Encoded as `<length>:<string>`, where length is a base ten value representing the length of the string following the colon.
 
 
**Integers**

Encoded as `i<number>e`.


**Lists**

Encoded as `l<elements>e`, where elements are Bencoded values themselves.


**Dictionaries**

Encoded as `d<elements>e`, where elements are alternating keys and values of any Bencoded type.

**Examples**

<pre>
<code class="python"># Byte Strings
8:announce => 'announce'
    
# Integers
i3e => 3
i-5e => -5
    
# Lists
l4:abcd3:efge => ['adcd', 'efg']
    
# Dictionaries
d13:creation datei1467011725e8:encoding5:UTF-8e => 
{'creation date': 1467011725, 'encoding': 'UTF-8'}</code>
</pre>
    
## Implementation

I decided to use Swift as my language of choice for this project, as I had not used it extensively before and I wanted to become more familiar with it. 

Swift's Enum type allowed me to create an elegant solution for representing Bencoded types internally.

<pre>
<code class="swift">enum BEncodedValue {
    case Dict(Dictionary<String, BEncodedValue>)
    case List([BEncodedValue])
    case Number(Int64)
    case Str([UInt8])
}</code>
</pre>

<small>
**N.B.** The reason that the Dict case type is *not* `Dictionary<BEncodedValue.Str, BEncodedValue>` is because per the BitTorrent specification, Bencoded Dictionaries must have valid UTF-8 strings as keys.</small>

From here, decoding a Bencoded string is a fairly straighforward process. Simply:

> Transform the input string into a stream of characters 
> 
> While there are characters left:
> 
> 1. Consume a character from the stream
> 2. Process accordingly (i.e. process the next set of characters depending on how the sequence begins) - mutating the stream
> 

Because of the definition of Bencoded values, the parsing will be recursive in nature as to parse a collection, the elements of the collection need to be parsed first. This idea translates quite literally into code:

<pre>
<code class="swift">
let dictionaryStart: UInt8  = [UInt8]("d".utf8)[0];      // 100
let dictionaryTerminator    = [UInt8]("e".utf8)[0];      // 101
let listStart: UInt8        = [UInt8]("l".utf8)[0];      // 108
let listTerminator: UInt8   = [UInt8]("e".utf8)[0];      // 101
let numberStart: UInt8      = [UInt8]("i".utf8)[0];      // 105
let numberTerminator: UInt8 = [UInt8]("e".utf8)[0];      // 101
let divider: UInt8          = [UInt8](":".utf8)[0];      // 58
    
    
func decode(contents: [UInt8]) -> BEncodedValue {
    // Turn input (list of bytes) into a stream of bytes
    var generator = contents.generate();
    let current = generator.next()!;
    
    // Parse the first byte
    return self.parse(current, generator: &generator);   
}
    
func parse(current: UInt8, inout generator: IndexingGenerator<[UInt8]>) -> BEncodedValue {
    /*
     * Takes a byte and parses a fraction of the byte stream 
     * as required based on the value of that byte. To parse 
     * a Dictionary or List, additional calls to this method
     * will be made. Base cases are when a Integer or Byte
     * String is encountered.
     */
    switch current {
    case dictionaryStart:
        return BEncodedValue.Dict(self.parseDictionary(&generator));
    
    case listStart:
        return BEncodedValue.List(self.parseList(&generator));
    
    case numberStart:
        return BEncodedValue.Number(self.parseNumber(&generator));
    
    default:
        return BEncodedValue.Str(self.parseByteArray(current, rest: &generator));
    }
}
</code>
</pre>

From here, the functions for parsing the different types as shown above need to be defined. I started with the `parseNumber()` function as it is one of two *base case* functions for the parser:

<pre>
<code>func parseNumber(inout contents: IndexingGenerator<[UInt8]>) -> Int64 {
    /*
     * Parses a BEncoded number from the data. A number is stored as a long
     * (Int64) due to the fact that it is used to store file size which
     * can exceed INT32_MAX.
     */
        
    var data: [UInt8] = [];
    
    // Consume a byte from the input stream until
    // the number termination character ("e") is met.
    while let current = contents.next() {
        if current == numberTerminator {
            break;
        }
        
        data.append(current);
    }
    
    // Interpret the bytes as a UTF-8 string...
    let bytesAsString = NSString(data: NSData(bytes: data as [UInt8],
                                              length: data.count),
                                 encoding: NSUTF8StringEncoding) as! String;
    
    // And cast to Int64
    return Int64(bytesAsString)!;
}</code>
</pre>

The second *base case* is parsing Byte Strings/Arrays which is defined by the `parseByteArray()` function as follows:

<pre>
<code>
func parseByteArray(first: UInt8, inout rest: IndexingGenerator<[UInt8]>) -> [UInt8] {
    /*
    * Parses a BEncoded string from the data. A string is simply a byte array
    * as it does not have any inherit encoding attached to it. A string has a
    * length component, denoting the length of the byte array, then the byte
    * array itself (i.e. length:contents).
    */  
    
    // The first byte of the length was already consumed
    // by the ``parse`` function, so we must account for it
    var lengthData: [UInt8] = [first];
    
    // Consume bytes (that comprise the length component of
    // the string) until the divider (":") is reached.
    while let current = rest.next() {
        if current == divider {
            break;
        }
    
        lengthData.append(current);
    }
    
    
    let lengthDataBytes = NSData(bytes: lengthData as [UInt8], length: lengthData.count);
        
    // Attempt to get a UTF-8 representation of the string
    let s: NSString? = NSString(data: lengthDataBytes, encoding: NSUTF8StringEncoding)
        
    // If we have a length string, try to interperet it as an Int
    guard s != nil else {
        return [UInt8]("Unable to decode string length".utf8)
    }
        
    let length = Int(s as! String)
        
    var data: [UInt8] = [];
    var cnt = 0;
        
    // Consume ``length`` bytes from the stream (i.e. the string value)
    while cnt < length! {
        let current = rest.next();
        
        data.append(current!);    
        cnt += 1;
    }
        
    return data;
}</code>
</pre>

Now that the base cases are taken care of, parsing lists and dictionaries is simple as they are just collections of other types. For Lists:

<pre>
<code>func parseList(inout contents: IndexingGenerator<[UInt8]>) -> [BEncodedValue] {
    /*
     * Parses a BEncoded list from the data.
     */
        
    var list = [BEncodedValue]();
        
    while let current = contents.next() {
        if current == listTerminator {
            break;
        }
            
        let value = self.parse(current, generator: &contents);
        list.append(value);
    }
        
    return list;
}</code>
</pre>

... and for Dictionaries: 

<pre>
<code>func parseDictionary(inout contents: IndexingGenerator<[UInt8]>) -> Dictionary<String, BEncodedValue> {
    /*
     *  Parses a BEncoded dictionary from the data.
     */
    
    var dict = [String: BEncodedValue]();
    var keys = [String]();
    
    while var current = contents.next() {
        if current == dictionaryTerminator {
            break;
        }
        
        // Read the key from the byte stream and interpret it
        // as it should be a valid UTF-8 string
        let data = self.parseByteArray(current, rest: &contents);
        let key = NSString(data: NSData(bytes: data as [UInt8], length: data.count),
                           encoding: NSUTF8StringEncoding) as? String;
        
        current = contents.next()!;
        let value = self.parse(current, generator: &contents);
        
        keys.append(key!);
        dict[key!] = value;
    }
    
    return dict;
}</code>
</pre>

And that is how to parse a Bencoded string using Swift!

I went on to add the functionality to export as JSON which was relatively straightforward due to how I chose to internally represent the Bencoded types.

The full source for my parser/serialiser (including a program for JSON output) can be found [here](https://gitlab.com/JedS6391/bencode-swift).
