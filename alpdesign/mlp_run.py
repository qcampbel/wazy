from functools import partial # for use with vmap
import jax
import jax.numpy as jnp
import haiku as hk
import jax.scipy.stats.norm as norm
import optax
from jax_unirep.layers import AAEmbedding, mLSTM, mLSTMAvgHidden
from jax_unirep.utils import load_params, load_embedding, seq_to_oh
from jax_unirep.utils import *
from jax_unirep import get_reps
import matplotlib.pyplot as plt
from jax.experimental import optimizers
from mlp import *


seqs = ['MSADDGIVYCQMRQGPWEFHIVTVESSAYDWVVVPGARIALDKYNAACEQHWSCILRRGIDQKPYAPDMLKCQCSDMCHPSDSFTWEIDAEAWYCNTDNLFTGIALYKNNDDYPDWYPIRCLKHKNVTAAQVPLVHFNDNKFTHHVHNDMPACDFKFFKTPTVRHACQFGSIYHSKQSRMDYSDLMQDEKAKHLKESHNVVPDDGIIIDPYMDILFGGRMNNREHCAKNE',
        'EKMHIKESATRMGFQYEYKLPYCIWAFIIGRAWHFVSLHGDQWDCWKMTFVIYSACSNGHIDGCEVQHANLSSGVLPARWFDAFQQNMKGFHKMKCGGFCTYAFLWGLAMRIYVRNMGNLAIYQNGGTSEWLTEFWYRLAGAVWPFKQFSINGECEHFWWSFHPFTLFDNPPAKDRNVTAYLHFDAHFYSIAMVWLMSPVVKGDSPVNCCAVDVEQSGESWALLNNWCAP',
        'HSFHKYKHGNWKSEGDQCLKVGQLRDECPQVNTPMYCSWGPHYFSIFHWIIPVAKAYHMLHNIEQQVYRCHWQERYKELHDATKTHQLEWSFGKSVWCAHCKPYIGWYRSPAGWHMPIKPPATKNLWVVRHKSKRKEGTISWENTLTCVWFHEICYGHGVCHQVHPWVVDSNEEYEMQWMETEVGECSYPAERQGAWYSFTQQQKWICIHVCNMSSGRVFCWYVLQLFRN',
        'LDHAVLKILQAMGPWNNRVEHPRLGKRSTEWPAAIYEGEPRWRLKCDTTATYYKAFETRWYNCHMTLTCWWHGATIRSKLTTMCMMVTNGYRDFYRYNDWKGRKATKHHPMVCIYEILWIAFMGCLHMWAGARVSKIWVGFCIFFASCLQMSPLKDWHNKCAFGRNNPLGMKGWGMMIGNSFCHIVHEMDNKYYAGAPVDEPFMYNQQVFGFGAMHCLCMADFCNEWGIQ',
        'PERHHYIGFHCYMQLDAIQQNPHWNAHVLFRAFDYVSNYWTWITMYDKYQGFLGIYVTSCKVHEHGACKHCHWPICYDCGQHADKMLWRKSFALHGQSHAYRPLWDRDLTGVLGISIDLNQGIKVAEAEGEILYCNVTDMTVMMHQSVGVFWCHDMAYPQWTDWYSSDNMMNSIPEISHMKNYRVTMVHEPLFIWECVSEWTENAEHEGHLITVGSTGGKWDTGMEREVM',
        'DPSQTIHCGTTGMSWGTMFKRSYILIIRYGTPEATCPCIVNCQIVVYWGCMFKKDRDPRGTPIQSTENFFKHAMMEPSYAGGTAHMEKEIEYRSQDSWHAYFSYWVKVWCYVCIALSQIPNVAHHGMHLHASPEDKKCANNWRFRYVAFIRIAHGCSWCYRECYNFRYDRYIAWNPVHLESVPEWWAHPAFEIVKDTVDDNQYSGADERQGDPIGGQPCLLCATWEDSWT',
        'LIDLFSLTRKFSRMPCRHNMNESYKEEWCETNNVKEYPHEQLLDKRYDIITLDGCKRMYCRSESQRITELHFIRYNMLCWPDRCIPLQYSQYESNMPPPMMRMWGCYHFGTLMFMSYAMPPTGEKREIVGGKEDHSGDLEDAFTDEDFNMDPAHQDYRHIAGTWHEPMFEIRMRYELTCNNMWSPIYANNAGMKQLTICNNDKICPTEGRRRQREIFNYKLHGRDQCQHI',
        'SCDVGPHPLHGQCTGMAKQVMETANIPQCPIDDHVTRATMGLIDAGACDRDRVCVREIWNVYYDKSTMKIIMDPPSDTCKHKSFYGDMMSHQQMGWLSECIIANMQHNLPWQLWESWMIHSEICMIKQRKVMMFCGIQSKYTEDFARFHPFILANTQYIIFKRPTTWPRVYAFLHRCMVLGWSAYGMTAMIPNTKETIKLAHCEKWPLTGSYTPSFVIFDGWLARKCQWP',
        'DWIEHVHTFWVLMFISNYPQIVCGLINQIEPWKSKFHSLAGFNQGCQCEKNYQGPIQAINGINQLVTITTPINNQENVDKKPHPGSVHTKSDAITLRFNQGVHNIFMWDMATQGRASIPFLNNMNGGGLTDYSWEQVVTCHCHMTNDLELDPQMLYMWWIVSANAWMVNGMRRQHMACHWAQWEGFRWPRYVQSVPMKVLLTTQKIHWMQYFREKFCFILMKWQGYWYTV',
        'RHWRAPLLMYRDKEVQITWHFRFMYHCDALTCSEVHCHARNFMVFGYSTPQNYNPVILYWVTWANTCLTPKGAYCARQMRMYATVTMSKINQMTITYLVDRQRQHWGLAFRSDNTCNHKWYLKHRCKVWNWGWLIDCYDLDRNLPKQVSRNQSSKSLRDLFNYIHYHWAMLPINIYCYSGDIWTTISTDDQFHIPTFIPCGKTVHEDLQPYEMCGMWHQCEDADYTMQPV',
]
labels = jnp.array([25.217391304347824,
                    15.652173913043478,
                    23.478260869565219,
                    22.173913043478262,
                    23.913043478260871,
                    24.782608695652176,
                    26.956521739130434,
                    17.391304347826086,
                    19.130434782608695,
                    26.521739130434781
                   ])
seqs = get_reps(seqs)[0]

config = Config()
key = jax.random.PRNGKey(0)



