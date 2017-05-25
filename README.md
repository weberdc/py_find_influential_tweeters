# py\_twitter\_analysis
An experimental project to analyse tweet data, specifically looking for signs of *"influence"*.

Current metrics generated are a variant on the academic h-index, an interactor ratio, a
retweet/mention ratio (more of a retweet/reply ratio really), a mixture model of retweeter/mention
ratio and interactor ratio called the _Social Network Potential_, all from a survey paper:

 * Riquelme, Fabián, and Pablo González-Cantergiani. "Measuring user influence on Twitter: A
   survey." Information Processing & Management 52, no. 5 (2016): 949-975.

Interactor ratio, _Ir_:

 * _Ir_ = `|unique retweeters/quoters/mentioners| / |followers|`

Retweet/Mention ratio, _RMr_

 * _RMr_ = `(|tweets retweeted or quoted| + |tweets replied to|) / |tweets posted|`

In addition to the SNP (0.25 * Ir + 0.75 * RMr), we include a mixture model which includes the
H-Index also: `(normalised(h-index) + normalised(Ir) + normalised(RMr)) / 3.0`

I included a measure of my own, which I call the post/activity ratio (_PAr_), which is intended
to measure the amount of activity inspired by tweets against the number of tweets posted (in the
corpus). I used 1, 2, 3, 1 as the default values for weights for retweets, quotes, replies and
favourites respectively.

 * _PAr_ = `(RT_weight * log(|retweets|) + QU_weight * log(|quotes|) + RE_weight * log(|replies|) + FAV_weight * log(|favourited|) / |tweets posted|`

Also included is a modification of the Duan-rank PageRank variant algorithm from a paper:

 * Duan, Y., et al. "An empirical study on learning to rank of tweets." Proceedings
   of the 23rd International Conference on Computational Linguistics. Association for
   Computational Linguistics, 2010.

The mixture model value normalises the three measures (within the observed ranges) and averages
them. It's not clear how valuable this measure is, because it assumes each measure is equally
valuable, which may not be the case.

# Usage
<pre>
$ bin/py_twitter_analysis
    -i|--input-file &lt;tweets_file.json&gt;  : File of tweets, one per line
    [-x|--max-iterations &lt;max loops&gt;]   : D-rank iteration roof value (default: 20)
    [-w|--weight &lt;weight factor value&gt;] : D-rank weighting factor (default: 0.2)
    [-c|--count &lt;tweet_count_limit&gt;]    : Only consider up to this many tweets (default: -1, all)
    [-v|--verbose]                      : Verbose debugging flag
</pre>

# Test Data
In the `data` directory are two test files, one, `qanda-100.json`, has 100 tweets including the `#qanda`
hashtag collected ABC's Q&A panel discussion from mid-August 2016 (the episode aired on the 15th of
August 2016). The other, `test.json`, is a hand-crafted set of 19 tweets by eight users, `@A`, `@B`,
`@C`, `@D`, `@E`, `@F`, `@G`, and `@H`.

User `@A` tweets four original tweets:

* `@A: tweet A1` (ID: `11`, follower count: 10)
* `@A: tweet A2` (ID: `12`, follower count: 10)
* `@A: tweet A3` (ID: `13`, follower count: 10)
* `@A: tweet A4 @B` (ID: `14`, mentioning: `@B`, favourited count: 10)

Users `@B`, `@C`, and `@D` all retweet `@A`'s first three tweets, resulting in:

* `@B: RT @A: tweet A1` (ID: `21`)
* `@B: RT @A: tweet A2` (ID: `22`)
* `@B: RT @A: tweet A3` (ID: `23`)
* `@C: RT @A: tweet A1` (ID: `31`)
* `@C: RT @A: tweet A2` (ID: `32`)
* `@C: RT @A: tweet A3` (ID: `33`)
* `@D: RT @A: tweet A1` (ID: `41`)
* `@D: RT @A: tweet A2` (ID: `42`)
* `@D: RT @A: tweet A3` (ID: `43`)

User `@E` replies to two of `@A`'s tweets:

* `@E: @A IKR (reply to @A1)` (ID: `51`, replying to tweet id: `1`)
* `@E: @A IKR (reply to @A2)` (ID: `52`, replying to tweet id: `2`)

User `@F` simply *mention*s `@A`:

* `@F: Tweeting about @A` (ID: `61`, mentions screen name: `@A`)

User `@G` *quote*s `@A`'s first tweet:

* `@G: Right on @A!` (ID: `71`, mentions screen name `@A`, includes URL to tweet `11` and expanded URL
  `https://twitter.com/A/status/11`)

User `@H` refers to an URL, and quotes a tweet mentioning another user:

* `@H: Look at https://t.co/short` (ID: `81`, includes URL `https://t.co/short` and expanded URL
  `https://some.com/expanded/url`)
* `@H: Right on @A!` (ID: `91`, mentions screen name `@A`, includes URL to tweet `14` and expanded URL
  `https://twitter/A/status/14` which itself mentions screen name `@B`

The expected output from is:

|User|@A |@B |others|
|----|:-:|:-:|:-:|
|h-index|3|0|0|
|Ir|0.6|0.2|0|
|RMr|1.5|0|0|
|SNP|1|0.08|0|
|Mixture|1|0.11|0|
|PAr|2.55|0|0|
|D-rank|4.06|2.5|0.8|

**NB** Users who do not interact with any other users (i.e. their tweets include no mentions, retweets
or quotes) will not have a D-Rank value. It can be assumed to be zero. Same with h-index values.

The JSON for the tweets in `test.json` aren't as populated as tweets that are delivered by Twitter itself.
I only included the fields and values that the code required, though I also included some fields that
were required by another analysis programme, separate from this project. The extra fields, of course,
don't affect the operation of this code, as they're simply ignored.
