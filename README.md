<h1>WebScout</h1>

<p>WebScout is a versatile network scanning tool designed to identify live web servers within specified IP ranges or networks. It allows users to customize scans with specific status codes and provides options for detailed server insights.</p>

<h2>Features</h2>

<ul>
  <li><strong>Customizable Status Codes</strong>: Specify which HTTP status codes should be considered to mark a server as "live."</li>
  <li><strong>Flexible Input Options</strong>: Accepts IP addresses from a file or standard input.</li>
  <li><strong>Concurrency Control</strong>: Manages multiple requests simultaneously, optimizing performance and speed.</li>
  <li><strong>Title Fetching</strong>: Optionally retrieve and display the title of web pages.</li>
</ul>

<h2>Installation</h2>

<p>Clone the repository to your local machine:</p>

<pre><code>git clone https://github.com/yourusername/webscout.git
cd webscout</code></pre>

<p>Ensure you have Python 3.x installed and install the required packages:</p>

<pre><code>pip install aiohttp beautifulsoup4</code></pre>

<h2>Usage</h2>

<h3>Basic Usage</h3>

<p>To scan a list of IPs from a file:</p>

<pre><code>python webscout.py -file ips.txt</code></pre>

<p>To specify custom HTTP status codes, specific concurrency and timeouts:</p>

<pre><code>python webscout.py -mc 200,302,404 -concurrency 20 -file ips.txt -timeout 4</code></pre>

<h3>Advanced Usage</h3>

<p>Show page titles and status codes:</p>

<pre><code>python webscout.py -title -status-code -file ips.txt</code></pre>

<h3>Chaining with Sanitizer</h3>

<p>First, use <code>sanitizer.py</code> to generate a clean list of IPs or URLs, then pipe it to <code>webscout.py</code>:</p>

<pre><code>python sanitizer.py "8.8.8.0/24 9.9.9.7 neopets.com 10.10.10.1-27" | python webscout.py</code></pre>

<p>This command processes mixed format addresses through <code>sanitizer.py</code>, producing a clean list, which is directly fed into <code>webscout.py</code> for scanning.</p>

<p>Example screenshots:</p>
<img width="462" alt="webscout" src="https://github.com/5u5urrus/WebScout/assets/165041037/a79b574f-fe0f-4322-aec3-d60075665ba6"><br>

<img width="462" alt="Screenshot 2024-06-23 023558" src="https://github.com/5u5urrus/WebScout/assets/165041037/6360e6cf-352d-4c4c-be3c-d5b15798b4be">


<h2>Contributing</h2>

<p>Contributions are welcome! Please feel free to submit a pull request or open an issue.</p>
