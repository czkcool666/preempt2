from preempt.ner import *
from preempt.sanitizer import *

device = (
    "mps" if torch.backends.mps.is_available() 
    else "cuda" if torch.cuda.is_available() 
    else "cpu"
)
# Load NER object && Load Sanitizer object
ner_model = NER("Universal-NER/UniNER-7B-all", device="cpu")
sanitizer = Sanitizer(ner_model, key = "FF4359D8D580AA4F7F036D6F04FC6A94", tweak = "E8E7920AFA330A73")

# assume the parent keys has already been encrypted. 
dependencies = {
 'key1': [8, None, 'base'],
 'key2': [3, None, 'base'],
 'key3': [5, None, 'base'],
 'key4': [24, ['key1', 'key2'], '(key1*key2)'],
 'key5': [36, ['key1', 'key3'], '(key1+key3)*3'],
 'key6': [11, ['key4'], '(key4/2 - 1)'],
 'key7': [33, ['key4', 'key5'], '(key4 + key5)'],
 'key8': [297, ['key6', 'key7', 'key2'], '(key6*key7) - key2'],
 'key9': [330, ['key8', 'key5'], '(key8 + key5)'],
 'key10': [109, ['key9', 'key3'], '(key9 - key3*3)'],
 'key11': [73, ['key10'], '(key10/1.5)'],
 'key12': [146, ['key11', 'key6'], '(key11 + key6*2)'],
 'key13': [219, ['key12', 'key7'], '(key12 + key7)'],
 'key14': [657, ['key13', 'key8'], '(key13*3 + key8/3)'],
 'key15': [876, ['key14', 'key9', 'key3'], '(key14 + key9 + key3*2)'],
 'key16': [438, ['key15'], '(key15/2)'],
 'key17': [514, ['key16', 'key10'], '(key16 + key10/2)'],
 'key18': [1028, ['key17', 'key12'], '(key17 + key12)'],
 'key19': [4112, ['key18', 'key14', 'key6'], '(key18*3 + key14 - key6)'],
 'key20': [3699, ['key19', 'key13'], '(key19 - key13*2)']
}


def main():
    base_keys = []   # make an empty list
    for k, v in dependencies.items():
        if v[2] == "base":
            base_keys.append(k)
            print(base_keys)
        else: 
            break

    for bk in base_keys:
        val, parents, relationship = dependencies[bk]
        extracted = ner_model.extract([str(val)+" years old"], entity_type='Age')
        print("extracted", extracted)
        sanitized, _= sanitizer.encrypt([str(val)+" years old"], entity='Age', epsilon=1, use_mdp=True, use_fpe=False)
        print("values after sanitizing:", sanitized)
        numInSanitized = float(sanitized[0].split()[0])
        dependencies[bk] = [numInSanitized, parents, relationship]
        print("what is stored in dependencies is: ", dependencies[bk])

    # can be improved by integrating more complicated flow rather than topdown tree
    for key, entry in dependencies.items():
        val, parents, relationship = dependencies[key]

        if relationship == "base":
            continue
        dic = {}
        for parent in parents:
            dic[parent] = float(dependencies[parent][0])
        dependencies[key] = [eval(relationship, {}, dic), parents, relationship]

    for key, entry in dependencies.items():
        print("finally", key, entry)


if __name__ == "__main__":
    main()



