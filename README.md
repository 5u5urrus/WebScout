<h1>WebScout</h1>

<p>
  WebScout is a versatile network scanning tool designed to identify live web servers within specified IP ranges or networks. It allows users to customize scans with specific status codes, choose custom ports, selectively scan over HTTP/HTTPS, and provides options for detailed server insights.
</p>

<h2>Features</h2>
<ul>
  <li><strong>Customizable Status Codes</strong>: Specify which HTTP status codes count as "live."</li>
  <li><strong>Flexible Input</strong>: Accepts IPs, domains, CIDR notation (e.g., <code>1.1.1.0/24</code>), and multi-octet ranges (e.g., <code>1.1.1-2.1-5</code>) from a file or standard input.</li>
  <li><strong>Custom Ports and Schemes</strong>: Check default or custom ports (e.g., <code>-p 8080,8443</code>) and choose HTTP, HTTPS, or both.</li>
  <li><strong>Concurrency Control</strong>: Manages multiple requests simultaneously, optimizing performance and speed.</li>
  <li><strong>Title Fetching</strong>: Optionally retrieve and display the <code>&lt;title&gt;</code> of web pages.</li>
</ul>

<h2>Installation</h2>

<p>Clone the repository to your local machine:</p>
<pre><code>git clone https://github.com/yourusername/webscout.git
cd webscout
</code></pre>

<p>Ensure you have Python 3.x installed and install the required packages (including <code>tqdm</code> for progress bars):</p>
<pre><code>pip install aiohttp beautifulsoup4 tqdm
</code></pre>

<h2>Usage</h2>

<h3>Basic Usage</h3>

<p>To scan a list of IPs from a file:</p>
<pre><code>python webscout.py -file ips.txt
</code></pre>

<p>To specify custom HTTP status codes, concurrency, and timeouts:</p>
<pre><code>python webscout.py -mc 200,302,404 -concurrency 20 -file ips.txt -timeout 4
</code></pre>

<h3>Show Page Titles and Status Codes</h3>
<pre><code>python webscout.py -title -status -file ips.txt
</code></pre>

<h3>Chaining with Sanitizer</h3>
<p>First, use <code>sanitizer.py</code> (optional script) to generate a clean list of IPs or URLs, then pipe it to <code>webscout.py</code>:</p>
<pre><code>python sanitizer.py "8.8.8.0/24 9.9.9.7 neopets.com 10.10.10.1-27" | python webscout.py
</code></pre>
<p>This processes mixed address formats through <code>sanitizer.py</code>, producing a clean list, which is directly fed into <code>webscout.py</code> for scanning.</p>

<h2>Advanced Usage</h2>

<h3>Specifying Custom Ports</h3>
<p>By default, WebScout checks ports <code>80</code> (HTTP) and <code>443</code> (HTTPS). If you want to scan additional or alternative ports, use:</p>
<pre><code>python webscout.py -p 8080,8443 -file ips.txt
</code></pre>
<p>
  For ports <code>80</code> and <code>443</code>, WebScout omits <code>:80</code> or <code>:443</code> from the URL.  
  For other ports (e.g., <code>8080</code>, <code>8443</code>), it tries both HTTP and HTTPS unless you select a different scheme (see below).
</p>

<h3>Selecting HTTP, HTTPS, or Both</h3>
<p>If you only want HTTP or only HTTPS, use:</p>
<pre><code># HTTP only
python webscout.py -p 8080,8443 -s http -file ips.txt

# HTTPS only
python webscout.py -p 8080,8443 -s https -file ips.txt
</code></pre>
<p>
  <code>-s http</code> will skip HTTPS checks entirely, even on <code>443</code>.  
  <code>-s https</code> will skip HTTP checks, including <code>80</code>.  
  <code>-s both</code> (default) scans both protocols for non-standard ports.
</p>

<h3>Multi-Octet Expansion</h3>
<p>WebScout supports IP ranges in multiple octets, for example:</p>
<pre><code>python webscout.py 1.1.1-2.1-5
</code></pre>
<p>
  This expands internally to:
  <br><code>1.1.1.1, 1.1.1.2, 1.1.1.3, 1.1.1.4, 1.1.1.5,
  1.1.2.1, 1.1.2.2, 1.1.2.3, 1.1.2.4, 1.1.2.5</code>
</p>

<h2>Example Screenshots</h2>

<p>Example screenshots:</p>
<img width="462" alt="webscout" src="https://github.com/5u5urrus/WebScout/assets/165041037/a79b574f-fe0f-4322-aec3-d60075665ba6"><br>
<img width="462" alt="Screenshot 2024-06-23 023558" src="https://github.com/5u5urrus/WebScout/assets/165041037/6360e6cf-352d-4c4c-be3c-d5b15798b4be">

<h2>Contributing</h2>
<p>Contributions are welcome! Please feel free to submit a pull request or open an issue.</p>
